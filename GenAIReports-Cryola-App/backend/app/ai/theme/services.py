import json
import base64
import re
import os
import httpx
import cv2
import numpy as np
import nest_asyncio
import asyncio
import asyncio
from typing import Optional
from io import BytesIO
from datetime import datetime
from app.core.config import settings

# Semantic Kernel
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.contents import ChatMessageContent, TextContent, ImageContent

from openai import AzureOpenAI

from .config import Config
from .models import EvaluatorOutput, FeedbackAnalyzerOutput
from .logger import get_logger
from .storage import BlobManager, encode_bytes_to_base64
from .prompts import EVALUATOR_INSTRUCTIONS, REFINEMENT_EVALUATOR_PROMPT, FEEDBACK_ANALYZER_INSTRUCTIONS

# Apply Asyncio patch
nest_asyncio.apply()

# ==========================================
# RENDERING SERVICES
# ==========================================

# -----------------------------
# WCAG Contrast Helpers
# -----------------------------
def srgb_to_linear(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

def relative_luminance(r, g, b):
    R = srgb_to_linear(r)
    G = srgb_to_linear(g)
    B = srgb_to_linear(b)
    return 0.2126 * R + 0.7152 * G + 0.0722 * B

def contrast_ratio(l1, l2):
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)

def pick_best_line_color(bgr_color):
    b, g, r = bgr_color
    fill_lum = relative_luminance(r, g, b)
    contrast_black = contrast_ratio(fill_lum, 0.0)
    contrast_white = contrast_ratio(fill_lum, 1.0)
    return (0, 0, 0) if contrast_black >= contrast_white else (255, 255, 255)

# ==========================================
# RENDERING SERVICES
# ==========================================

def render_gpt_images_in_memory(client: AzureOpenAI, source_bytes: bytes, prompt: str, folder_name: str, n: int, phase: str, line_color: tuple[int, int, int] = (0, 0, 0)) -> list[str]:
    logger = get_logger("ThemeEngine_Services")
    storage = BlobManager()
    uploaded_urls = []
    
    try:
        logger.info(f"Rendering {n} image(s) with GPT...")
        
        # Prepare input stream
        input_stream = BytesIO(source_bytes)
        input_stream.name = "input.jpeg"

        # Call API without forcing response_format 
        result = client.images.edit(
            model=Config.IMAGE_MODEL,
            image=input_stream,
            prompt=prompt,
            input_fidelity = "high",
            quality = "high",
            size="1536x1024",
            n=n,
        )
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        with httpx.Client() as http_client:
            for idx, image_data in enumerate(result.data, 1):
                filename = f"{phase}_v{idx}_{timestamp}.jpg"
                img_bytes = None
                
                # --- ROBUST DATA EXTRACTION ---
                if getattr(image_data, 'url', None):
                    logger.info("Extracting image via URL download...")
                    try:
                        resp = http_client.get(image_data.url)
                        resp.raise_for_status()
                        img_bytes = resp.content
                    except Exception as e:
                        logger.error(f"Failed to download from Azure URL: {e}")
                        continue
                
                elif getattr(image_data, 'b64_json', None):
                    logger.info("Extracting image via Base64 decode...")
                    try:
                        img_bytes = base64.b64decode(image_data.b64_json)
                    except Exception as e:
                        logger.error(f"Failed to decode Base64: {e}")
                        continue
                
                else:
                    logger.error(f"API returned unknown format. Available fields: {dir(image_data)}")
                    continue

                if img_bytes:
                    blob_path = f"project/{folder_name}/{filename}"
                    url = storage.upload_bytes(img_bytes, blob_path)
                    uploaded_urls.append(url)
                    logger.info(f"Saved: {filename}")
            
        return uploaded_urls

    except Exception as e:
        logger.error(f"GPT Render failed: {e}", exc_info=True)
        return []



async def render_single_variant_theme(
    client: AzureOpenAI, 
    source_bytes: bytes, 
    prompt: str, 
    folder_name: str, 
    phase: str, 
    index: int,
    line_color: tuple[int, int, int] = (0, 0, 0)
) -> Optional[str]:
    """
    Async wrapper for single image generation + upload.
    Executes blocking calls (API + Upload) in threads to allow concurrency.
    """
    logger = get_logger("ThemeEngine_Services")
    storage = BlobManager()
    
    try:
        logger.info(f"Starting generic render task {phase} index {index}...")

        # 1. Run sync API call in thread
        def blocking_api_call():
            # Create fresh stream for thread safety
            input_stream = BytesIO(source_bytes)
            input_stream.name = "input.jpeg"
            return client.images.edit(
                model=Config.IMAGE_MODEL,
                image=input_stream,
                prompt=prompt,
                input_fidelity="high",
                quality="high",
                size="1536x1024",
                n=1,
            )

        result = await asyncio.to_thread(blocking_api_call)

        if not result.data:
            return None

        image_data = result.data[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{phase}_v{index}_{timestamp}.jpg"
        img_bytes = None

        # 2. Extract Data (Async/Sync mix)
        if getattr(image_data, 'url', None):
            async with httpx.AsyncClient() as http_client:
                resp = await http_client.get(image_data.url)
                resp.raise_for_status()
                img_bytes = resp.content
        elif getattr(image_data, 'b64_json', None):
            img_bytes = base64.b64decode(image_data.b64_json)

        if img_bytes:
            blob_path = f"project/{folder_name}/{filename}"
            # 3. Upload (locking/sync) call in thread
            url = await asyncio.to_thread(storage.upload_bytes, img_bytes, blob_path)
            logger.info(f"Saved: {filename}")
            return url
            
    except Exception as e:
        logger.error(f"Single Variant Render failed: {e}")
        return None


def render_opencv_in_memory(source_bytes: bytes, hex_code: str, folder_name: str, line_color: tuple[int, int, int]) -> str:
    """
    Single callable function.
    Takes image bytes + hex color + determined line color.
    Returns saved image path.
    """
    
    # Use global logger and BlobManager (imported from .logger and .storage)
    logger = get_logger("ThemeEngine_Services")
    storage = BlobManager()

    # -----------------------------
    # Execution Starts Here
    # -----------------------------
    try:
        logger.info("Rendering with OpenCV (Production Grade)...")

        nparr = np.frombuffer(source_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Decode failed")

        # HEX to BGR
        bgr_color = tuple(int(hex_code.lstrip('#')[i:i+2], 16) for i in (4, 2, 0))


        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        thresh = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,
            15,
            5
        )

        kernel = np.ones((3, 3), np.uint8)
        closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(
            closed,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        filled = np.ones_like(img) * 255

        cv2.drawContours(
            filled,
            contours,
            -1,
            bgr_color,
            thickness=cv2.FILLED
        )

        line_mask = cv2.inRange(gray, 0, 80)

        result = filled.copy()
        result[line_mask == 255] = line_color

        success, buffer = cv2.imencode(".jpeg", result)
        if not success:
            raise ValueError("Encode failed")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"opencv_{timestamp}.jpeg"
        # Match GPT function path structure
        blob_path = f"project/{folder_name}/{filename}"
        
        url = storage.upload_bytes(buffer.tobytes(), blob_path)
        logger.info(f"Saved: {filename}")
        return url

    except Exception as e:
        logger.error(f"OpenCV failed: {e}")
        return None

# ==========================================
# AGENT SERVICES
# ==========================================

def create_evaluator() -> ChatCompletionAgent:
    kernel = Kernel()
    service = AzureChatCompletion(
        deployment_name=Config.CRITIC_GPT_MODEL,
        endpoint=settings.AZURE_OPENAI_ENDPOINT,
        api_key=settings.AZURE_OPENAI_API_KEY,
        api_version=Config.GPT_API_VERSION
    )
    kernel.add_service(service)
    
    return ChatCompletionAgent(kernel=kernel, instructions=EVALUATOR_INSTRUCTIONS, name="Evaluator")

def create_refinement_evaluator() -> ChatCompletionAgent:
    kernel = Kernel()
    service = AzureChatCompletion(
        deployment_name=Config.CRITIC_GPT_MODEL,
        endpoint=settings.AZURE_OPENAI_ENDPOINT,
        api_key=settings.AZURE_OPENAI_API_KEY,
        api_version=Config.GPT_API_VERSION
    )
    kernel.add_service(service)
    return ChatCompletionAgent(kernel=kernel, instructions=REFINEMENT_EVALUATOR_PROMPT, name="RefineEval")

def create_feedback_analyzer() -> ChatCompletionAgent:
    kernel = Kernel()
    service = AzureChatCompletion(
        deployment_name=Config.GPT_MODEL,
        endpoint=settings.AZURE_OPENAI_ENDPOINT,
        api_key=settings.AZURE_OPENAI_API_KEY,
        api_version=Config.GPT_API_VERSION
    )
    kernel.add_service(service)
    return ChatCompletionAgent(kernel=kernel, instructions=FEEDBACK_ANALYZER_INSTRUCTIONS, name="FeedbackAnalyzer")

async def evaluate_images_batch(evaluator, ref_url, generated_urls, hex_code, prompt):
    storage = BlobManager()
    ref_bytes = await storage.download_image_to_bytes(ref_url)
    items = [
        TextContent(text=f"Prompt: {prompt}\nTarget Hex: {hex_code}"),
        TextContent(text="Reference:"),
        ImageContent(uri=encode_bytes_to_base64(ref_bytes))
    ]
    for idx, url in enumerate(generated_urls):
        gen_bytes = await storage.download_image_to_bytes(url)
        items.append(TextContent(text=f"Image ID: {url}")) # Mapping key
        items.append(ImageContent(uri=encode_bytes_to_base64(gen_bytes)))
        
    message = ChatMessageContent(role="user", items=items)
    resp_text = ""
    async for resp in evaluator.invoke([message]): resp_text += str(resp.content)
    
    try:
        cleaned = re.sub(r'```json\s*|\s*```', '', resp_text)
        match = re.search(r'\{.*\}', cleaned, re.DOTALL)
        if match: return EvaluatorOutput.model_validate_json(match.group())
    except: pass
    return EvaluatorOutput(evaluation=[], regenerate_required="yes")

async def evaluate_single_image(evaluator, ref_bytes: bytes, gen_url: str, hex_code: str, prompt: str, pid: str) -> dict:
    logger = get_logger("ThemeEngine_Services")
    try:
        storage = BlobManager()
        gen_bytes = await storage.download_image_to_bytes(gen_url)
        
        items = [
            TextContent(text=f"Prompt: {prompt}\nTarget Hex: {hex_code}"),
            TextContent(text="Reference:"),
            ImageContent(uri=encode_bytes_to_base64(ref_bytes)),
            TextContent(text=f"Image ID: {pid}"),
            ImageContent(uri=encode_bytes_to_base64(gen_bytes))
        ]
        
        message = ChatMessageContent(role="user", items=items)
        resp_text = ""
        async for resp in evaluator.invoke([message]): resp_text += str(resp.content)
        
        score = 0
        feedback = ""
        
        try:
            cleaned = re.sub(r'```json\s*|\s*```', '', resp_text)
            match = re.search(r'\{.*\}', cleaned, re.DOTALL)
            if match:
                output = EvaluatorOutput.model_validate_json(match.group())
                if output.evaluation:
                    item = output.evaluation[0]
                    score = item.confidence_score
                    feedback = item.feedback
        except Exception as e:
            logger.error(f"Evaluation parsing failed for {pid}: {e}")
            
        return {
            "id": pid,
            "url": gen_url,
            "score": score,
            "feedback": feedback
        }
    except Exception as e:
        logger.error(f"Single image evaluation failed for {pid}: {e}")
        return {
            "id": pid,
            "url": gen_url,
            "score": 0,
            "feedback": f"Evaluation failed: {str(e)}"
        }