
import os
import mimetypes
import base64
import json
import re
import asyncio
from PIL import Image
from typing import Dict, List, Any, Optional
import tempfile
import aiohttp

from app.ai.product.prompts import (
    PRODUCT_ANNOTATION_AGENT_PROMPT, 
    PRODUCT_INITIAL_GENERATION_PROMPT, 
    PRODUCT_INITIAL_CRITIC_PROMPT, 
    PRODUCT_INITIAL_CRITIC_USER_PROMPT,
    PRODUCT_REFINEMENT_PROMPTER_AGENT_PROMPT,
    PRODUCT_REFINEMENT_PROMPTER_AGENT_PROMPT,
    get_product_refinement_prompter_agent_user_prompt,
    PRODUCT_REFINEMENT_CRITIC_PROMPT,
    get_product_refinement_critic_user_prompt,
    PRODUCT_USER_REFINEMENT_REGEN_PROMPTER_PROMPT,
    get_product_user_refinement_regen_prompter_user_prompt
)
from app.ai.product.config import product_config
from app.core.config import settings
from app.ai.graphics.logger import get_logger
from app.ai.product.storage import BlobManager

import semantic_kernel as sk
from semantic_kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.contents import ChatMessageContent, TextContent, ImageContent
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from openai import AzureOpenAI

logger = get_logger("Product_Services")

# ------------------------------------------
# SK Agent Factory
# ------------------------------------------
def create_sk_agent(deployment: str, system_prompt: str, name: str):
    kernel = Kernel()
    svc = AzureChatCompletion(
        deployment_name=deployment,
        endpoint=settings.AZURE_OPENAI_ENDPOINT,
        api_key=settings.AZURE_OPENAI_API_KEY,
        api_version=product_config.AZURE_API_VERSION
    )
    kernel.add_service(svc)

    return ChatCompletionAgent(
        kernel=kernel,
        instructions=system_prompt,
        name=name
    )

# ------------------------------------------
# Image Model Client
# ------------------------------------------
def get_image_client():
    return AzureOpenAI(
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        api_key=settings.AZURE_OPENAI_API_KEY,
        api_version=product_config.AZURE_API_VERSION
    )


logger = get_logger("Product_Services")

# ------------------------------------------
# Helpers
# ------------------------------------------

async def download_file_to_temp(url: str) -> str:
    """Downloads a file from a URL to a temp file and returns the path."""
    if not url.startswith("http"):
        return url # Already local
        
    try:
        blob_mgr = BlobManager()
        # If BlobManager has optimize download, use it, else raw request
        # Since BlobManager.download_image_to_bytes handles auth/blob logic:
        data = await blob_mgr.download_image_to_bytes(url)
        
        # Create temp file
        ext = url.split('.')[-1].split('?')[0]
        if len(ext) > 4: ext = "png" # Fallback
        
        fd, path = tempfile.mkstemp(suffix=f".{ext}")
        with os.fdopen(fd, 'wb') as f:
            f.write(data)
        return path
    except Exception as e:
        logger.error(f"Failed to download {url}: {e}")
        raise e

async def download_assets_to_local(urls: List[str]) -> List[str]:
    """Downloads a list of URLs to local temp files."""
    tasks = [download_file_to_temp(u) for u in urls]
    return await asyncio.gather(*tasks)

# ------------------------------------------
# Image Prompt Mapper
# ------------------------------------------
class ImagePromptMapper:
    """
    Deterministic mapper for semantic image placeholders.

    Supported placeholders:
    - CURRENT_OUTPUT_IMAGE_URL
    - BASE_DISPLAY_UNIT_IMAGE_URL
    - PRODUCT_A_IMAGE_URL
    - PRODUCT_B_IMAGE_URL
    - PRODUCT_C_IMAGE_URL (optional)
    - PRODUCT_D_IMAGE_URL (optional)
    """

    SUPPORTED_PLACEHOLDERS = {
        "CURRENT_OUTPUT_IMAGE_URL",
        "BASE_DISPLAY_UNIT_IMAGE_URL",
        "PRODUCT_A_IMAGE_URL",
        "PRODUCT_B_IMAGE_URL",
        "PRODUCT_C_IMAGE_URL",
        "PRODUCT_D_IMAGE_URL",
        "PRODUCT_E_IMAGE_URL",
        "PRODUCT_F_IMAGE_URL",
        "PRODUCT_G_IMAGE_URL",
        "PRODUCT_H_IMAGE_URL"
    }

    def extract_placeholders(self, prompt: str) -> List[str]:
        """
        Extract semantic placeholders from the prompt in order of appearance.
        """
        found = []
        seen = set()

        for match in re.finditer(r'\b[A-Z_]+_IMAGE_URL\b', prompt):
            placeholder = match.group(0)
            if placeholder in self.SUPPORTED_PLACEHOLDERS and placeholder not in seen:
                found.append(placeholder)
                seen.add(placeholder)

        return found

    def map_prompt_to_images(
        self,
        prompt: str,
        image_urls: Dict[str, str]
    ) -> Dict[str, Dict]:
        """
        Map semantic placeholders to actual image URLs.

        Args:
            prompt: Prompt containing semantic placeholders
            image_urls: Dict of {PLACEHOLDER_NAME: url}

        Returns:
            Mapping with strict validation info
        """
        placeholders = self.extract_placeholders(prompt)

        mappings = {}

        for placeholder in placeholders:
            if placeholder not in image_urls:
                logger.warning(f"Missing required image URL for placeholder: {placeholder}")
                continue

            mappings[placeholder] = {
                "matched_variable": placeholder,
                "url": image_urls[placeholder],
                "valid": True
            }

        return mappings

# ------------------------------------------
# Service Functions
# ------------------------------------------

def encode_file(file_path: str) -> str:
    """
    Encodes a local file to base64 data URI, or returns the URL if it's http/s.
    """
    if file_path.startswith("http"):
        return file_path
        
    try:
        with open(file_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            ext = file_path.split('.')[-1]
            if ext.lower() == "jpg": ext = "jpeg"
            return f"data:image/{ext};base64,{encoded_string}"
    except Exception as e:
        logger.error(f"Error encoding file {file_path}: {e}")
        raise e

async def run_annotation_agent_sk(fsdu_image_path: str, product_image_paths: List[str], product_dimensions: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyzes FSDU structure and product dimensions to generate a layout annotation using Semantic Kernel.
    """
    logger.info("Starting Annotation Agent...")
    
    agent = create_sk_agent(
        deployment=product_config.REASONING_MODEL,
        system_prompt=PRODUCT_ANNOTATION_AGENT_PROMPT,
        name="AnnotationAgent"
    )

    try:
        encoded_fsdu = encode_file(fsdu_image_path)
        
        # Build message content
        items = [
            TextContent(text="Analyze the FSDU + products + dimensions and generate product-aware annotation JSON."),
            ImageContent(uri=encoded_fsdu),
            TextContent(text=json.dumps({"product_dimensions": product_dimensions}))
        ]

        for path in product_image_paths:
            encoded_prod = encode_file(path)
            items.append(ImageContent(uri=encoded_prod))
            
        msg = ChatMessageContent(role="user", items=items)

        out = ""
        async for response in agent.invoke([msg]):
            if response.content:
                out += str(response.content)

        # Parse JSON
        raw = out
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            clean_json_str = match.group(0)
            parsed = json.loads(clean_json_str)
            logger.info("Annotation JSON generated successfully.")
            return parsed
        else:
            logger.error("No JSON object found in response")
            return {"error": "No JSON object found", "raw_response": raw}

    except Exception as e:
        logger.exception(f"Annotation Agent failed: {e}")
        return {"error": str(e)}

async def generate_prompt_sk(
    annotation_json: Dict[str, Any],
    base_display_unit_url: str,
    product_image_urls: List[str]
) -> str:
    """
    Generates the compositing prompt using Semantic Kernel.
    """
    logger.info("Starting Prompt Generation...")
    
    agent = create_sk_agent(
        deployment=product_config.REASONING_MODEL,
        system_prompt=PRODUCT_INITIAL_GENERATION_PROMPT,
        name="PrompterAgent"
    )

    try:
        text_content = (
            "SECTION: INPUT_METADATA\n\n"
            "IMAGE_ORDER (STRICT):\n"
            "- IMAGE_1: BASE_DISPLAY_UNIT (IMMUTABLE)\n"
            "- IMAGE_2..N: PRODUCT_IMAGES (FRONT-FACING)\n\n"
            "ANNOTATION_JSON (AUTHORITATIVE):\n"
            f"{json.dumps(annotation_json, indent=2)}\n\n"
            "TASK:\n"
            "Using the annotation JSON as the SINGLE SOURCE OF TRUTH,\n"
            "generate ONE final GPT-IMAGE-1.5 EDIT PROMPT.\n\n"
            "OUTPUT CONSTRAINTS:\n"
            "- Output MUST be plain text only\n"
            "- Do NOT include analysis, JSON, markdown, or explanations\n"
            "- Do NOT restate system rules\n"
            "- The output prompt must be directly usable in GPT-IMAGE-1.5 EDIT\n\n"
        )

        items = [
            TextContent(text=text_content),
            ImageContent(uri=base_display_unit_url)
        ]
        
        for url in product_image_urls:
            items.append(ImageContent(uri=url))

        msg = ChatMessageContent(role="user", items=items)

        out = ""
        async for response in agent.invoke([msg]):
            if response.content:
                out += str(response.content)
        
        return out.strip().strip('"')

    except Exception as e:
        logger.exception(f"Prompt Generation failed: {e}")
        return f"Error generating prompt: {e}"

async def run_critic_sk(
    generation_prompt: str,
    base_image_path: str,
    generated_img_path: str,
    product_image_paths: List[str]
) -> Dict[str, Any]:
    """
    Evaluates the generated image using Semantic Kernel.
    """
    
    agent = create_sk_agent(
        deployment=product_config.REASONING_MODEL,
        system_prompt=PRODUCT_INITIAL_CRITIC_PROMPT,
        name="CriticAgent"
    )

    try:       
        # 1. Base Image
        if base_image_path.startswith("http"):
            base_image_path = await download_file_to_temp(base_image_path)
            
        # 2. Generated Image
        if generated_img_path.startswith("http"):
            generated_img_path = await download_file_to_temp(generated_img_path)
            
        # 3. Product Images
        prod_urls_local = []
        for p in product_image_paths:
             if p.startswith("http"):
                 prod_urls_local.append(await download_file_to_temp(p))
             else:
                 prod_urls_local.append(p)
                 
        base_url = encode_file(base_image_path)
        gen_url = encode_file(generated_img_path)
        prod_urls = [encode_file(p) for p in prod_urls_local]
        
        user_prompt_filled = PRODUCT_INITIAL_CRITIC_USER_PROMPT.format(prompt=generation_prompt)

        items = [
            ImageContent(uri=base_url), # Image 1
        ]
        
        # Product Images (start from Image 2)
        for url in prod_urls:
            items.append(ImageContent(uri=url))
            
        # Output Image (Last)
        items.append(ImageContent(uri=gen_url))
        
        # Text Prompt
        items.append(TextContent(text=user_prompt_filled))

        msg = ChatMessageContent(role="user", items=items)
        
        out = ""
        async for response in agent.invoke([msg]):
            if response.content:
                out += str(response.content)

        raw = out.strip()
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            clean_json = match.group(0)
            data = json.loads(clean_json)
             # Ensure confidence_score is present
            if "confidence_score" not in data:
                 data["confidence_score"] = 0
            
            # Normalize score if needed
            if data["confidence_score"] <= 1.0:
                 data["confidence_score"] *= 100
                 
            return data
        else:
            logger.error("No JSON found in critic response")
            return {"error": "No JSON found", "raw": raw, "confidence_score": 0}

    except Exception as e:
        logger.exception(f"SK Critic failed: {e}")
        return {"error": str(e), "confidence_score": 0}



async def generate_product_refinement_plan_sk(
    user_feedback: str,
    current_output_image_url: str,
    base_image_url: str,
    product_image_urls: List[str]
) -> str:
    """
    Generates a refined prompt based on user feedback using Semantic Kernel.
    """
    logger.info("Starting Refinement Prompt Generation...")
    
    agent = create_sk_agent(
        deployment=product_config.REASONING_MODEL,
        system_prompt=PRODUCT_REFINEMENT_PROMPTER_AGENT_PROMPT,
        name="RefinementAgent"
    )

    try:
        # User Prompt
        text_content = get_product_refinement_prompter_agent_user_prompt(
            user_feedback=user_feedback
        )

        # Image Order:
        # 1. Current Output (Editable Base)
        # 2. Base FSDU
        # 3... Products
        
        items = [
            TextContent(text=text_content),
            ImageContent(uri=current_output_image_url),
            ImageContent(uri=base_image_url)
        ]
        
        for url in product_image_urls:
            items.append(ImageContent(uri=url))

        msg = ChatMessageContent(role="user", items=items)

        out = ""
        async for response in agent.invoke([msg]):
            if response.content:
                out += str(response.content)
        
        return out.strip().strip('"')

    except Exception as e:
        logger.exception(f"Refinement Generation failed: {e}")
        return f"Error generating refinement prompt: {e}"

async def generate_patch_refinement_plan_sk(
    original_prompt: str,
    evaluation_result_json: Dict[str, Any]
) -> str:
    """
    Generates a patched prompt using the Edit Patch Agent.
    """
    logger.info("Starting Patch Refinement Generation...")
    
    agent = create_sk_agent(
        deployment=product_config.REASONING_MODEL,
        system_prompt=PRODUCT_USER_REFINEMENT_REGEN_PROMPTER_PROMPT,
        name="PatchAgent"
    )

    try:
        # Prepare Inputs
        eval_str = json.dumps(evaluation_result_json, indent=2)
        
        user_prompt_text = get_product_user_refinement_regen_prompter_user_prompt(
            original_prompt=original_prompt,
            evaluation_result=eval_str
        )
        
        msg = ChatMessageContent(role="user", items=[TextContent(text=user_prompt_text)])

        out = ""
        async for response in agent.invoke([msg]):
            if response.content:
                out += str(response.content)
        
        # Parse JSON
        raw = out.strip()
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            clean_json = match.group(0)
            data = json.loads(clean_json)
            return data.get("patched_prompt", raw) # Return raw if key missing (fallback)
        else:
            logger.error("No JSON found in patch response")
            return raw # Return raw text if parsing fails

    except Exception as e:
        logger.exception(f"Patch Generation failed: {e}")
        return original_prompt # Fallback to original if patch fails

async def evaluate_product_refinement_result_sk(
    generation_prompt: str,
    generated_img_path: str,
    base_image_path: str,
    product_image_paths: List[str]
) -> Dict[str, Any]:
    """
    Evaluates the refined image against user feedback using Semantic Kernel.
    """
    
    agent = create_sk_agent(
        deployment=product_config.REASONING_MODEL,
        system_prompt=PRODUCT_REFINEMENT_CRITIC_PROMPT,
        name="RefinementCritic"
    )

    try:       
        if base_image_path.startswith("http"):
            base_image_path = await download_file_to_temp(base_image_path)
            
        if generated_img_path.startswith("http"):
            generated_img_path = await download_file_to_temp(generated_img_path)
            
        prod_urls_local = []
        for p in product_image_paths:
             if p.startswith("http"):
                 prod_urls_local.append(await download_file_to_temp(p))
             else:
                 prod_urls_local.append(p)
                 
        base_url = encode_file(base_image_path)
        gen_url = encode_file(generated_img_path)
        prod_urls = [encode_file(p) for p in prod_urls_local]
        
        user_prompt_filled = get_product_refinement_critic_user_prompt(
            new_prompt=generation_prompt
        )

        items = [
            ImageContent(uri=base_url), # Image 1
        ]
        
        # Product Images
        for url in prod_urls:
            items.append(ImageContent(uri=url))
            
        # Output Image (Last)
        items.append(ImageContent(uri=gen_url))
        
        # Text Prompt
        items.append(TextContent(text=user_prompt_filled))

        msg = ChatMessageContent(role="user", items=items)
        
        out = ""
        async for response in agent.invoke([msg]):
            if response.content:
                out += str(response.content)

        raw = out.strip()
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            clean_json = match.group(0)
            data = json.loads(clean_json)
            if "confidence_score" not in data:
                 data["confidence_score"] = 0
            
            if data["confidence_score"] <= 1.0:
                 data["confidence_score"] *= 100
                 
            return data
        else:
            logger.error("No JSON found in refinement critic response")
            return {"error": "No JSON found", "raw": raw, "confidence_score": 0}

    except Exception as e:
        logger.exception(f"Refinement Critic failed: {e}")
        return {"error": str(e), "confidence_score": 0}


# ------------------------------------------
# Helper Functions
# ------------------------------------------

async def batch_convert_to_inches(image_paths: List[str]) -> Dict[str, Any]:
    """Calculates dimensions in inches for a list of image paths or URLs."""
    
    # Pre-download any URLs
    local_paths = []
    # Map original path/url to local path
    path_map = {} 
    
    urls_to_download = [p for p in image_paths if p.startswith("http")]
    downloaded = {}
    if urls_to_download:
        dl_paths = await download_assets_to_local(urls_to_download)
        for url, local in zip(urls_to_download, dl_paths):
            downloaded[url] = local
            
    results = {}
    for image_path in image_paths:
        try:
            # Resolve to local path
            target_path = downloaded.get(image_path, image_path) 
            
            # Handle empty or invalid paths
            if not target_path or not os.path.exists(target_path):
                results[os.path.basename(image_path) if image_path else "unknown"] = {'error': "File not found"}
                continue

            img = Image.open(target_path)
            width_px, height_px = img.size
            dpi = img.info.get('dpi', (300, 300))
            dpi_x, dpi_y = dpi
            
            width_inches = width_px / dpi_x
            height_inches = height_px / dpi_y
            
            filename = os.path.basename(image_path) # Use original filename as key
            results[filename] = {
                'width_inches': round(width_inches, 2),
                'height_inches': round(height_inches, 2),
                'aspect_ratio': round(width_px / height_px, 2)
            }
        except Exception as e:
            print(f" Error processing {image_path}: {e}")
            filename = os.path.basename(image_path) if image_path else "unknown"
            results[filename] = {'error': str(e)}
    return results

async def parse_placement_data_complete(json_input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parses backend JSON, calculates real dimensions, maps Image Indices,
    and returns a consolidated JSON object.
    """
    logger.info("Parsing placement data")
    try:
        placement_data = json_input.get('details', {}).get('products', {}).get('placement', [])
    except AttributeError:
        return {"error": "Invalid JSON structure"}

    # --- STEP A: Collect & Process Unique Images ---
    unique_paths_set = set()
    for tray in placement_data:
        for product in tray:
            path = product.get('image', '')
            if path:
                unique_paths_set.add(path)

    # Calculate real dimensions for all unique assets
    unique_paths_list = list(unique_paths_set)
    dim_cache = await batch_convert_to_inches(unique_paths_list)

    # Sort for deterministic "Image X" indexing (Image 1 = FSDU, start at 2)
    sorted_unique_assets = sorted(unique_paths_list)
    index_map = {path: f"Image {i + 2}" for i, path in enumerate(sorted_unique_assets)}

    # --- STEP B: Build Blueprint & Summary ---
    blueprint = {} 
    for tray_idx, tray_products in enumerate(placement_data, start=1):
        tray_key = f"tray_{tray_idx}"
        blueprint[tray_key] = []
        
        product_count = len(tray_products)

        for prod_idx, product in enumerate(tray_products, start=1):
            full_path = product.get('image', '')
            filename = os.path.basename(full_path) if full_path else "unknown"
            
            # Get Image Reference (e.g., "Image 2")
            image_ref = index_map.get(full_path, "MISSING_ASSET")

            # Get Real Dimensions from Cache (Fallback to JSON defaults if error)
            dims = dim_cache.get(filename, {})
            if "error" not in dims and dims:
                w_in = dims['width_inches']
                h_in = dims['height_inches']
                aspect = dims['aspect_ratio']
            else:
                # Fallback to JSON data if file read failed
                json_dims = product.get('dimensions', [])
                w_in = next((d['value'] for d in json_dims if d['name'] == 'Width'), 0)
                h_in = 0 # JSON didn't have height in example
                aspect = 0

            # Add to Blueprint
            slot_entry = {
                "slot_id": f"{tray_key}_s{prod_idx}",
                "image_ref": image_ref,
                "filename": filename,
                "width_inches": w_in,
                "height_inches": h_in,
                "physical_aspect_ratio": aspect,
                "stack_count": product.get('stack_count', 3)
            }
            blueprint[tray_key].append(slot_entry)
            
    # --- STEP C: Consolidate Output ---
    final_output = {
        "unique_assets": sorted_unique_assets,
        "blueprint": blueprint
    }
    
    return final_output
