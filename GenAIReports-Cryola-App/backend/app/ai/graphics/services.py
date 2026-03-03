# ------------------------------------------
# Imports
# ------------------------------------------
import json
import asyncio
import base64
from typing import List, Dict, Any, Optional, Tuple
import re
import os

import semantic_kernel as sk
from semantic_kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.contents import ChatMessageContent, TextContent, ImageContent
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from openai import AzureOpenAI
from app.core.config import settings
from .config import config
from .prompts import (
    GRAPHICS_INITIAL_REGION_ANALYZER_PROMPT,
    GRAPHICS_INITIAL_ANNOTATION_PROMPT, 
    GRAPHICS_INITIAL_PROMPTER_PROMPT,
    GRAPHICS_INITIAL_CRITIQUE_PROMPT,
    GRAPHICS_REFINEMENT_PROMPTER_PROMPT,
    GRAPHICS_REFINEMENT_EVALUATOR_PROMPT
)
from .utils import encode_bytes_to_base64, make_output_filename
from .storage import BlobManager
from .logger import get_logger

logger = get_logger("Graphics_Services")

# ------------------------------------------
# SK Agent Factory
# ------------------------------------------
def create_sk_agent(deployment: str, system_prompt: str, name: str):
    kernel = Kernel()
    svc = AzureChatCompletion(
        deployment_name=deployment,
        endpoint=settings.AZURE_OPENAI_ENDPOINT,
        api_key=settings.AZURE_OPENAI_API_KEY,
        api_version=config.AZURE_API_VERSION
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
        api_version=config.AZURE_API_VERSION
    )

# ----------------------------------------------------
# BUILD SYSTEM PROMPT FOR ACTIVE GRAPHICS (DYNAMIC)
# ----------------------------------------------------
# ----------------------------------------------------
# ARCHITECTURE ANALYZER
# ----------------------------------------------------
async def run_architecture_analyzer(base_image_bytes: bytes) -> Dict[str, Any]:
    """
    Analyzes the base structure image to dynamically generate region specs (descriptions).
    """
    logger.info("-----Architecture Analyzer phase started-----")
    
    agent = create_sk_agent(
        deployment=config.REASONING_MODEL,
        system_prompt=GRAPHICS_INITIAL_REGION_ANALYZER_PROMPT,
        name="ArchitectureAnalyzer"
    )

    base_b64 = encode_bytes_to_base64(base_image_bytes)
    
    user_prompt = """
        Analyze the attached display unit image.

        Follow all SYSTEM-level rules and constraints exactly; do not override or reinterpret them.

        For each component label listed below:
        1. Select the appropriate `id` strictly from the ALLOWED COMPONENT IDS defined in the SYSTEM prompt.
        2. Write a short, precise description (1–2 sentences) that describes only the physical shape, visual boundary, and form of the component.
        - The description must allow automated models to unambiguously identify the component without referencing or mentioning any other components.

        Rules:
        - Do NOT reference or describe other components.
        - Do NOT use marketing or standardized names.
        - Do NOT include placement notes, measurements, materials, branding references, or rendering instructions.
        - Avoid ambiguous or comparative wording.
        - Treat each component as a standalone, clearly isolated physical region.
        - Return ONLY valid JSON in the OUTPUT FORMAT defined in the SYSTEM prompt.

        Component labels:
        - Top Header Panel
        - Left Side Panel
        - Tray Guard Lip / Front Rails
        - Base / Bottom Plinth
        """
    
    items = [
        TextContent(text=user_prompt),
        ImageContent(uri=base_b64)
    ]
    
    msg = ChatMessageContent(role="user", items=items)
    
    try:
        out = ""
        async for response in agent.invoke([msg]):
            if response.content:
                out += str(response.content)
        
        # Robust JSON extraction
        cleaned_out = out.replace("```json", "").replace("```", "").strip()
        start_idx = cleaned_out.find('{')
        end_idx = cleaned_out.rfind('}')
        if start_idx != -1 and end_idx != -1:
             cleaned_out = cleaned_out[start_idx : end_idx + 1]
             
        return json.loads(cleaned_out)

    except Exception as e:
        logger.error(f"Architecture Analyzer failed: {e}")
        # Fallback to static specs if dynamic fails? 
        # For now, let's raise or return empty to fail fast
        raise e


# ----------------------------------------------------
# BUILD SYSTEM PROMPT FOR ACTIVE GRAPHICS
# ----------------------------------------------------
def build_annotation_system_prompt(active_keys: list, dynamic_specs: Dict = None):
    # If dynamic specs provided, use them. Else fallback to static REGION_SPECS
    # Region Specs
    REGION_SPECS_STATIC = {
        "Header_Graphic": {
            "id": "Top_Header_Panel",
            "desc": "The top fascia/header panel.",
            "rule": "Center aligned. Do not crop. Maintain header structure."
        },
        "Front_Lip_Graphic": {
            "id": "Front_Lip_Rails",
            "desc": "The thin front facing strips/retainers on every shelf level.",
            "rule": "Repeat logic: Apply to ALL shelf lips. No cropping. Fit to height."
        },
        "Left_Side_Panel_Graphic": {
            "id": "Left_Side_Panel",
            "desc": "The vertical side panels/wings of the display.",
            "rule": "Full height placement. Watch for perspective skew."
        },
        "Right_Side_Panel_Graphic": {
            "id": "Right_Side_Panel",
            "desc": "The vertical side panels/wings of the display.",
            "rule": "Full height placement. Watch for perspective skew."
        },
        "Base_Plinth_Graphic": {
            "id": "Base_Plinth_Panel",
            "desc": "A flat quadrilateral base panel with straight perimeter edges and a slightly angled top surface, forming a shallow wedge-like rectangle..",
            "rule": "Locate absolute quadrilateral base panel with straight perimeter edges and a slightly angled top surface"
        }
    }
    specs_source = dynamic_specs if dynamic_specs else REGION_SPECS_STATIC
    
    # build region text list
    # The dynamic_specs structure - REGION_SPECS: { 'Key': {'id':..., 'desc':...} }
    region_text = "\n".join([
        f"- {specs_source[k]['id']} : {specs_source[k]['desc']}"
        for k in active_keys if k in specs_source
    ])

    # inject region list into template
    final_prompt = GRAPHICS_INITIAL_ANNOTATION_PROMPT.replace("<<<REGION_LIST>>>", region_text)
    return final_prompt

# ----------------------------------------------------
# ANNOTATION AGENT INVOCATION 
# ----------------------------------------------------
async def generate_layout_annotations_robust(
    active_keys: list, 
    active_assets_data: dict, 
    base_image_data: bytes,
    region_specs: Dict = None 
):
    """
    active_assets_data: Dict[str, bytes] -> key to image bytes
    base_image_data: bytes of base shelf
    region_specs: Optional dynamic specs from Architecture Analyzer
    """
    logger.info("-----Annotatation phase started-----")
    sys_prompt = build_annotation_system_prompt(active_keys, dynamic_specs=region_specs)

    agent = create_sk_agent(
        deployment=config.REASONING_MODEL, 
        system_prompt=sys_prompt,
        name="AnnotationAgent"
    )

    # send the BASE SHELF IMAGE
    items = [
        TextContent(text=f"Active graphics: {active_keys}. Produce JSON annotation."),
        ImageContent(uri=encode_bytes_to_base64(base_image_data))
    ]

    # send each graphic image
    for k in active_keys:
        img_bytes = active_assets_data[k]
        items.append(ImageContent(uri=encode_bytes_to_base64(img_bytes)))

    user_msg = ChatMessageContent(role="user", items=items)

    try:
        # run agent
        out = ""
        async for response in agent.invoke([user_msg]):
            if response.content:
                out += str(response.content)

        # Robust JSON extraction
        cleaned_out = out.replace("```json", "").replace("```", "").strip()
        
        # Sometimes models output text before/after
        start_idx = cleaned_out.find('{')
        end_idx = cleaned_out.rfind('}')
        
        if start_idx != -1 and end_idx != -1:
             cleaned_out = cleaned_out[start_idx : end_idx + 1]
             
        return json.loads(cleaned_out)
    except Exception as e:
        logger.exception(f"Graphics Annotation failed. Error: {e}")
        # Re-raise to let pipeline fail fast
        raise e

# ----------------------------------------------------
# JSON → INSTRUCTION TEXT PARSER 
# ----------------------------------------------------
def parse_annotations_to_string(annotation_json: dict) -> str:
    logger.info("-----Parsing annotataions started-----")
    try:
        if not annotation_json:
            return "No annotation generated."
        
        final = []

        shelf_struct = annotation_json.get("shelf_structure", {})
        perspective = shelf_struct.get("perspective_analysis", {})

        final.append(
            f"GLOBAL SCENE CONTEXT:\n"
            f"CAMERA ANGLE: {perspective.get('camera_angle','unknown')}\n"
            f"DISTORTION LEVEL: {perspective.get('perspective_distortion_level','unknown')}\n"
        )

        components = {c["id"]: c for c in shelf_struct.get("components", [])}

        for m in annotation_json.get("component_asset_mapping", []):
            region = m.get("shelf_component_id")
            asset = m.get("graphic_asset_name")
            scale = m.get("scaling_policy","unknown")
            steps = " ".join(m.get("compositing_instructions", []))

            comp = components.get(region, {})
            poly = comp.get("perspective_polygon_norm")
            bbox = comp.get("bounding_box_norm")

            geo = f"QUAD: {poly}" if poly else f"BBOX: {bbox}"

            final.append(
                f"\nLOCATION: {region}\n"
                f"GEOMETRY: {geo}\n"
                f"ASSET: {asset}\n"
                f"SCALING POLICY: {scale}\n"
                f"ACTION: {steps}\n"
            )

        return "\n".join(final)
    except Exception as e:
        logger.error(f"Error parsing Graphics annotations: {e}")
        return "Error parsing annotations."


# ------------------------------------------
# PROMPT GENERATION 
# ------------------------------------------
async def generate_graphics_prompt(annotation_instructions, images_encoded_list):
    logger.info("-----GraphicsPrompter phase started-----")
    agent = create_sk_agent(
        deployment=config.REASONING_MODEL,
        system_prompt=GRAPHICS_INITIAL_PROMPTER_PROMPT,
        name="GraphicPrompter"
    )

    msg_items = [TextContent(text=f"annotation_instructions:\n{annotation_instructions}")]
    for img_uri in images_encoded_list:
        msg_items.append(ImageContent(uri=img_uri))

    msg = ChatMessageContent(role="user", items=msg_items)

    try:
        out = ""
        async for response in agent.invoke([msg]):
            if response.content:
                out += str(response.content)
        # Strip outer quotes if present
        return out.strip().strip('"')
    except Exception as e:
        logger.exception(f"Graphics prompt generation failed. Error: {e}")
        raise e

# ------------------------------------------
# RENDERING
# ------------------------------------------
async def render_single_variant(image_client, images_for_render_tuples, prompt, blob_manager: BlobManager, output_filename: str):
    """
    images_for_render_tuples: list of (filename, bytes)
    """ 
    try:
        result = await asyncio.to_thread(
            image_client.images.edit,
            model=config.IMAGE_MODEL,
            input_fidelity="high",
            quality="high",
            size = "1536x1024",
            image=images_for_render_tuples,      # list of (filename, bytes)
            prompt=prompt,
            n=1
        )

        img_b64 = result.data[0].b64_json
        img_bytes = base64.b64decode(img_b64)

        # Upload via BlobManager
        url = blob_manager.upload_bytes(img_bytes, output_filename, content_type="application/octet-stream")
        return url, img_bytes
    except Exception as e:
        logger.exception(f"Graphics Image rendering failed for {output_filename}. Error: {e}")
        raise e

# ------------------------------------------
# CRITIC
# ------------------------------------------
def generate_constraint_block(critique: Dict[str, Dict]) -> str:
    lines = []
    for dimension, detail in critique.items():
        recs = detail.get("recommendations", [])
        if not recs:
            continue
        lines.append(f"[{dimension.upper()}]")
        for r in recs:
            lines.append(f"- {r}")
    return "\n".join(lines)

def apply_critic_to_prompt(user_prompt: str, critique_json: Dict) -> str:
    block = generate_constraint_block(critique_json)
    refined = f"""
            {user_prompt}

            ------------------------------------------------------------
            AUTO-APPLIED CRITIQUE RECOMMENDATIONS
            ------------------------------------------------------------
            {block}
            ------------------------------------------------------------
            END OF AUTO-APPLIED CRITIQUE RECOMMENDATIONS
            """
    return refined.strip()

async def run_critic(
    user_prompt: str,
    base_img_b64: str,
    rendered_img_b64: str,
    graphic_assets_b64: List[str],
    client
) -> Dict:
    
    agent = create_sk_agent(
        deployment=config.REASONING_MODEL,
        system_prompt=GRAPHICS_INITIAL_CRITIQUE_PROMPT,
        name="CriticAgent"
    )

    items = []
    
    # Header
    items.append(TextContent(text=(
        "IMAGE INPUTS BEGIN — ORDER IS STRICT AND POSITIONAL\n\n"
        "1. IMAGE_1 -> BASE_DISPLAY_UNIT\n"
        "2. IMAGE_2 -> OUTPUT_IMAGE\n"
        "3. IMAGE_3..N -> GRAPHIC_ASSETS\n\n"
        "Any deviation, omission, or reordering MUST be treated as an evaluation failure."
    )))

    # Images
    items.append(ImageContent(uri=base_img_b64))
    items.append(ImageContent(uri=rendered_img_b64))
    
    for asset_b64 in graphic_assets_b64:
        items.append(ImageContent(uri=asset_b64))

    # Prompt
    items.append(TextContent(text=(
        "TEXT_INPUT → USER_PROMPT\n\n"
        f"{user_prompt}\n\n"
        "This prompt defines expected placements and constraints."
    )))

    msg = ChatMessageContent(role="user", items=items)

    try:
        out = ""
        async for response in agent.invoke([msg]):
            if response.content:
                out += str(response.content)

        # Cleanup json markdown
        cleaned_out = out.replace("```json", "").replace("```", "").strip()
        return json.loads(cleaned_out)

    except Exception as e:
        logger.exception(f"Graphics Initial Critic evaluation failed. Error: {e}")
        raise e



async def evaluate_variants_with_critic(
    variant_results: list, # list of dicts {url, bytes}
    user_prompt: str,
    base_img_bytes: bytes,
    graphic_asset_bytes_list: list, # list of bytes
    client
):
    base_b64 = encode_bytes_to_base64(base_img_bytes)
    asset_b64_list = [encode_bytes_to_base64(b) for b in graphic_asset_bytes_list]

    async def eval_single(variant):
        rendered_b64 = encode_bytes_to_base64(variant["bytes"])

        critique = await run_critic(
            user_prompt=user_prompt,
            base_img_b64=base_b64,
            rendered_img_b64=rendered_b64,
            graphic_assets_b64=asset_b64_list,
            client=client
        )

        scores = [
            critique["structural_integrity"]["confidence_score"],
            critique["placement_accuracy"]["confidence_score"],
            critique["graphics_integrity"]["confidence_score"],
        ]
        overall = sum(scores) / 3

        # Aggregate feedback
        feedback = []
        feedback.extend(critique["structural_integrity"].get("recommendations", []))
        feedback.extend(critique["placement_accuracy"].get("recommendations", []))
        feedback.extend(critique["graphics_integrity"].get("recommendations", []))

        return {
            "url": variant["url"],
            "critique": critique,
            "overall_score": overall,
            "feedback": feedback
        }

    return await asyncio.gather(*[eval_single(v) for v in variant_results])


# ------------------------------------------
# USER REFINEMENT SERVICES
# ------------------------------------------

class ImagePromptMapper:
    """
    Maps placeholder names in prompts to actual image variable names.
    Uses keyword matching to find the right image for each placeholder.
    """
    
    def __init__(self):
        self.keyword_rules = {
            'output': ['output', 'current_output'],
            'display_unit': ['display', 'unit', 'base_display'],
            'header': ['header', 'top'],
            'rail': ['rail', 'strip'],
            'bottom': ['bottom', 'base', 'footer', 'plinth'],
            'side': ['side', 'lateral'],
        }
    
    def extract_placeholders(self, prompt: str) -> List[str]:
        """
        Extract all placeholders from prompt:
        - IMAGE_N patterns
        - Bracketed placeholders [PLACEHOLDER]
        - Plain uppercase placeholders with underscores
        """
        placeholders_in_order = []
        seen = set()

        # Match IMAGE_1, [PLACEHOLDER], or UPPERCASE_UNDERSCORE words
        for match in re.finditer(r'\[([A-Z_]+)\]|IMAGE_(\d+)|\b([A-Z_]{2,})\b', prompt):
            if match.group(1):
                placeholder = match.group(1)
            elif match.group(2):
                placeholder = f'IMAGE_{match.group(2)}'
            elif match.group(3):
                placeholder = match.group(3)
            else:
                continue

            if placeholder not in seen:
                placeholders_in_order.append(placeholder)
                seen.add(placeholder)

        return placeholders_in_order

    def find_keywords_in_text(self, text: str) -> List[str]:
        """Find which keywords appear in the given text"""
        text_lower = text.lower()
        found_keywords = []

        for keyword, variants in self.keyword_rules.items():
            for variant in variants:
                if variant in text_lower:
                    found_keywords.append(keyword)
                    break

        return found_keywords

    def match_placeholder_to_variable(self, placeholder: str, available_vars: List[str]) -> Tuple[str, List[str]]:
        """
        Match a placeholder to the best matching variable name.
        Returns (best_match_variable, [all_candidates])
        """
        placeholder_keywords = self.find_keywords_in_text(placeholder)
        scored_vars = []

        for var in available_vars:
            var_keywords = self.find_keywords_in_text(var)
            common_keywords = set(placeholder_keywords) & set(var_keywords)
            score = len(common_keywords)
            scored_vars.append((var, score, list(common_keywords)))

        # Sort descending by score
        scored_vars.sort(key=lambda x: x[1], reverse=True)

        best_match = scored_vars[0][0] if scored_vars and scored_vars[0][1] > 0 else None
        candidates = [(var, score, keywords) for var, score, keywords in scored_vars if score > 0]

        return best_match, candidates

    def map_prompt_to_images(self, prompt: str, image_paths: Dict[str, str]) -> Dict[str, Dict]:
        """
        Map all placeholders in prompt to available image paths.
        Returns a dictionary mapping placeholder -> matched variable info.
        """
        placeholders = self.extract_placeholders(prompt)
        available_vars = list(image_paths.keys())

        mappings = {}
        for placeholder in placeholders:
            best_match, candidates = self.match_placeholder_to_variable(placeholder, available_vars)
            mappings[placeholder] = {
                'matched_variable': best_match,
                'file_path': image_paths.get(best_match) if best_match else None,
                'all_candidates': candidates,
                'placeholder_keywords': self.find_keywords_in_text(placeholder)
            }

        return mappings

# Refinement Plan Generation
async def generate_refinement_plan(
    user_feedback: str,
    base_display_b64: str,
    current_output_b64: str,
    graphic_asset_b64_list: List[str]
) -> Dict[str, Any]:
    
    logger.info("---- Graphics Orchestrator Refinement phase started-----")
    
    agent = create_sk_agent(
        deployment=config.REASONING_MODEL,
        system_prompt=GRAPHICS_REFINEMENT_PROMPTER_PROMPT,
        name="RefinementPlanAgent"
    )

    # Text Input
    text_input = (
        f"SECTION: INPUT_METADATA\n"
        f"IMAGE_ORDER: IMAGE_1: BASE_DISPLAY_UNIT, IMAGE_2: CURRENT_OUTPUT_IMAGE, IMAGE_3..N: GRAPHIC_ASSETS\n"
        f"USER_FEEDBACK_TEXT:\n{user_feedback}"
    )
    
    items = [TextContent(text=text_input)]
    
    # Images
    # Order: Base, Output, Assets (matching prompt instruction)
    items.append(ImageContent(uri=encode_bytes_to_base64(base_display_b64) if isinstance(base_display_b64, bytes) else base_display_b64))
    items.append(ImageContent(uri=encode_bytes_to_base64(current_output_b64) if isinstance(current_output_b64, bytes) else current_output_b64))
    
    for i, asset in enumerate(graphic_asset_b64_list):
         uri = encode_bytes_to_base64(asset) if isinstance(asset, bytes) else asset
         items.append(ImageContent(uri=uri))
        
    msg = ChatMessageContent(role="user", items=items)
    
    try:
        out = ""
        async for response in agent.invoke([msg]):
            if response.content:
                out += str(response.content)
        
        #logger.info(f"Orchestrator Raw Output:\n{out}")
        return out
        
    except Exception as e:
        logger.exception(f"Graphics Refinement Orchestrator failed. Error: {e}")
        raise e


async def evaluate_refinement_result(
    old_image_bytes: bytes,
    new_image_bytes: bytes,
    instruction_prompt: str,
    client
) -> Dict:
     
    old_b64 = encode_bytes_to_base64(old_image_bytes)
    new_b64 = encode_bytes_to_base64(new_image_bytes)

    agent = create_sk_agent(
        deployment=config.REASONING_MODEL,
        system_prompt=GRAPHICS_REFINEMENT_EVALUATOR_PROMPT,
        name="RefinementEvaluator"
    )

    items = [
        ImageContent(uri=old_b64),
        ImageContent(uri=new_b64),
        TextContent(text=instruction_prompt)
    ]
    
    msg = ChatMessageContent(role="user", items=items)

    try:
        out = ""
        async for response in agent.invoke([msg]):
            if response.content:
                out += str(response.content)
        
        # Cleanup json markdown just in case, though structure usually matches
        cleaned_out = out.replace("```json", "").replace("```", "").strip()
        return json.loads(cleaned_out)
    except Exception as e:
        logger.exception(f"Graphics Refinement evaluation failed. Error: {e}")
        return {"confidence_score": 0, "feedback": ["Evaluation failed."]}



