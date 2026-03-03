
import os
import base64
import json
import asyncio
import mimetypes
from datetime import datetime
from io import BytesIO
import tempfile
import aiohttp
from typing import Dict, List, Any, Optional
from PIL import Image
from app.core.config import settings
import semantic_kernel as sk
from semantic_kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.functions.kernel_arguments import KernelArguments
from semantic_kernel.contents import ChatMessageContent, TextContent, ImageContent
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, AzureChatPromptExecutionSettings
from openai import AzureOpenAI

from app.ai.multi_angle.config import product_config
from app.ai.multi_angle.logger import get_logger
from app.ai.multi_angle.storage import BlobManager
from app.ai.multi_angle.multi_angle_prompts import (
    L2R_PROMPT_WITH_SP,
    L2R_PROMPT_WITHOUT_SP,
    L2R_CRITIC_SYSTEM_PROMPT,
    L2R_CRITIC_USER_PROMPT,
    STRAIGHT_VIEW_PROMPT_CONSTRUCTOR_SYSTEM_PROMPT,
    STRAIGHT_VIEW_CRITIC_SYSTEM_PROMPT,
    STRAIGHT_VIEW_CRITIC_USER_PROMPT
)

logger = get_logger("MultiAngle_Services")

# ------------------------------------------
# Helpers
# ------------------------------------------

def encode_image(path: str) -> str:
    """Encodes a local file to base64 data URI."""
    if path.startswith("http"):
        return path
        
    mime, _ = mimetypes.guess_type(path)
    if mime is None:
        mime = "image/png" # Default fallback
    
    try:
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
            return f"data:{mime};base64,{b64}"
    except Exception as e:
        logger.error(f"Failed to encode image {path}: {e}")
        raise e

async def download_file_to_temp(url: str) -> str:
    """Downloads a file from a URL to a temp file and returns the path."""
    if not url.startswith("http"):
        return url # Already local
        
    try:
        blob_mgr = BlobManager()
        data = await blob_mgr.download_image_to_bytes(url)
        
        # Create temp file
        ext = url.split('.')[-1].split('?')[0]
        if len(ext) > 4 or "/" in ext: ext = "png" # Fallback
        
        fd, path = tempfile.mkstemp(suffix=f".{ext}")
        with os.fdopen(fd, 'wb') as f:
            f.write(data)
        return path
    except Exception as e:
        logger.error(f"Failed to download {url}: {e}")
        raise e

# ------------------------------------------
# SK Agent Factory
# ------------------------------------------
def create_sk_agent(deployment: str, system_prompt: str, name: str) -> ChatCompletionAgent:
    kernel = Kernel()
    
    # Use config values
    endpoint = settings.AZURE_OPENAI_ENDPOINT
    api_key = settings.AZURE_OPENAI_API_KEY
    
    svc = AzureChatCompletion(
        deployment_name=deployment,
        endpoint=endpoint,
        api_key=api_key,
        api_version=product_config.AZURE_API_VERSION
    )
    kernel.add_service(svc)

    return ChatCompletionAgent(
        kernel=kernel,
        instructions=system_prompt,
        name=name
    )

def get_image_client():
    return AzureOpenAI(
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        api_key=settings.AZURE_OPENAI_API_KEY,
        api_version=product_config.AZURE_API_VERSION
    )

# ------------------------------------------
# Service Functions
# ------------------------------------------
async def generate_image_azure(
    folder_name: str,
    prompt: str,
    input_image_path: str,
    output_prefix: str,
    run_idx: int
) -> Optional[str]:
    """
    Generates an image using Azure OpenAI (GPT-Image).
    """
    logger.info(f"Generating image ({output_prefix} run {run_idx})...")
    client = get_image_client()
    
    try:
        # Prepare input path (handle blob url)
        effective_input_path = input_image_path
        if input_image_path.startswith("http"):
            effective_input_path = await download_file_to_temp(input_image_path)
            
        def _call_api_sync(path):
             with open(path, "rb") as f:
                return client.images.edit(
                    model=product_config.IMAGE_MODEL,
                    input_fidelity="high",
                    quality="high",
                    #size="1536x1024",
                    image=f,
                    prompt=prompt,
                    n=1
                )
        
        result = await asyncio.to_thread(_call_api_sync, effective_input_path)
        
        # Cleanup temp file if we created one
        if effective_input_path != input_image_path and os.path.exists(effective_input_path):
            try:
                os.remove(effective_input_path)
            except: pass
        
        item = result.data[0]
        image_bytes = base64.b64decode(item.b64_json)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{output_prefix}_{run_idx}_{timestamp}.png"
        blob_path = f"project/{folder_name}/{filename}"

        if input_image_path.startswith("http"):
            # Rule 1: Blob Input -> Try Blob Storage (via BlobManager)
            # BlobManager handles Azure if configured, else falls back to local
            blob_mgr = BlobManager()
            saved_path = blob_mgr.upload_bytes(image_bytes, blob_path, content_type="application/octet-stream")
            
            if saved_path and saved_path.startswith("file://"):
                 return saved_path.replace("file://", "")
            return saved_path
            
        else:
            # Rule 2: Local Input -> Force Local Output
            output_dir = product_config.OUTPUT_DIR
            output_dir.mkdir(parents=True, exist_ok=True)
            
            file_path = output_dir / filename
            with open(file_path, "wb") as f:
                f.write(image_bytes)
                
            return str(file_path)

    except Exception as e:
        logger.error(f"Image generation failed for {output_prefix} run {run_idx}: {e}")
        return None

async def evaluate_l2r_image_sk(
    output_path: str,
    input_image_path: str,
    edit_prompt: str
) -> Dict[str, Any]:
    """
    Evaluates L2R image using Semantic Kernel.
    """
    return await _evaluate_image_generic(
        output_path, 
        input_image_path, 
        edit_prompt, 
        L2R_CRITIC_SYSTEM_PROMPT, 
        L2R_CRITIC_USER_PROMPT
    )

async def evaluate_straight_view_image_sk(
    output_path: str,
    input_image_path: str,
    edit_prompt: str
) -> Dict[str, Any]:
    """
    Evaluates Straight View image using Semantic Kernel.
    """
    return await _evaluate_image_generic(
        output_path, 
        input_image_path, 
        edit_prompt, 
        STRAIGHT_VIEW_CRITIC_SYSTEM_PROMPT, 
        STRAIGHT_VIEW_CRITIC_USER_PROMPT
    )

async def _evaluate_image_generic(
    output_path: str,
    input_image_path: str,
    edit_prompt: str,
    system_prompt: str,
    user_prompt_template: str
) -> Dict[str, Any]:
    
    if not output_path:
        return {"error": "No output path provided"}
        
    logger.info(f"Evaluating {output_path}...")
    try:
        # Resolve images (handle blob url)
        effective_input = input_image_path
        effective_output = output_path
        
        if input_image_path.startswith("http"):
            effective_input = await download_file_to_temp(input_image_path)
            
        if output_path.startswith("http"):
            effective_output = await download_file_to_temp(output_path)

        input_url = encode_image(effective_input)
        output_url = encode_image(effective_output)
        
        agent = create_sk_agent(
            deployment=product_config.REASONING_MODEL,
            system_prompt=system_prompt,
            name="CriticAgent"
        )
        
        items = [
            TextContent(text=user_prompt_template),
            TextContent(text=f"EDIT PROMPT:\n{edit_prompt}"),
            ImageContent(uri=input_url),
            ImageContent(uri=output_url)
        ]
        
        msg = ChatMessageContent(role="user", items=items)
        
        out = ""
        settings = AzureChatPromptExecutionSettings(temperature=0.0)
        kernel_args = KernelArguments(settings=settings)
        async for response in agent.invoke([msg], arguments=kernel_args):
            if response.content:
                out += str(response.content)
        
        content = out.strip()
        # Clean JSON markdown
        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
            
        result_json = json.loads(content.strip())
        
        return {
            "output_path": output_path,
            "score": result_json.get("confidence_score"),
            "feedback": result_json.get("feedback")
        }
        
    except Exception as e:
        logger.error(f"Evaluation failed for {output_path}: {e}")
        return {
            "output_path": output_path,
            "error": str(e)
        }
