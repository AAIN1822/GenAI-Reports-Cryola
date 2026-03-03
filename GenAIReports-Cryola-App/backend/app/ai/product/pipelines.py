import json
import re
import base64
import asyncio
import os
from typing import Dict, Any, List
import datetime
from app.ai.graphics.logger import get_logger
from app.core.config import settings
from .config import product_config
from .services import (
    get_image_client,
    run_annotation_agent_sk,
    generate_prompt_sk,
    run_critic_sk,
    parse_placement_data_complete,
    encode_file,
    download_assets_to_local,
    generate_product_refinement_plan_sk,
    evaluate_product_refinement_result_sk,
    ImagePromptMapper,
    generate_patch_refinement_plan_sk
)
from .storage import BlobManager

logger = get_logger("Product_Pipelines")

def format_duration(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.2f}s"
    minutes = int(seconds // 60)
    remaining = seconds % 60
    return f"{minutes}m {remaining:.2f}s"

async def generate_composite_image(
    folder_name: str,
    prompt: str,
    base_image_path: str,
    product_image_paths: List[str],
    variant_idx: int = 0,
    attempt: int = 0,
    step: str = "initial"
) -> str:
    """
    Calls Azure OpenAI to generate the composited image.
    Downloads inputs if needed. Uploads output to Blob.
    Returns the URL/Path to the saved output image.
    """
    client = get_image_client()
    blob_mgr = BlobManager()
    download_start = time.perf_counter()
    local_base = (await download_assets_to_local([base_image_path]))[0]
    local_products = await download_assets_to_local(product_image_paths)
    download_end = time.perf_counter()
    download_duration = download_end - download_start
    logger.info(f"Downloaded inputs for image generation took {format_duration(download_duration)}")
    files = []
    try:
        try:
             files.append(open(local_base, "rb"))
             for p in local_products:
                 files.append(open(p, "rb"))
        except Exception as e:
             for f in files: f.close()
             raise e

        # Call API
        try:
            ai_start = time.perf_counter()
            result = await asyncio.to_thread(
                client.images.edit,
                model=product_config.IMAGE_MODEL,
                input_fidelity="high",
                quality="high",
                size = "1536x1024",
                image=files,
                prompt=prompt,
                n=1
            )
            
            # Process Result
            item = result.data[0]
            if not item.b64_json:
                raise ValueError("No b64_json in response")
                
            image_bytes = base64.b64decode(item.b64_json)
            ai_end = time.perf_counter()
            ai_duration = ai_end - ai_start
            logger.info(f"AI Image generation took {format_duration(ai_duration)}")
            # Upload to storage
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"product_{step}_attempt{attempt}_var{variant_idx}_{timestamp}.png"
            blob_path = f"project/{folder_name}/{filename}"
            
            # BlobManager to upload bytes
            # It handles local fallback if creds missing
            upload_start = time.perf_counter()
            nav_url = blob_mgr.upload_bytes(image_bytes, blob_path, content_type="application/octet-stream")
            upload_end = time.perf_counter()
            upload_duration = upload_end - upload_start
            logger.info(f"Uploaded generated image took {format_duration(upload_duration)}")
            if nav_url:
                logger.info(f"Image generated and uploaded to {nav_url}")
                return nav_url
            else:
                raise Exception("Upload failed")

        finally:
            for f in files:
                f.close()

    except Exception as e:
        logger.exception(f"Image generation failed: {e}")
        return f"Error generating image: {e}"

import time
async def run_product_placement_initial_pipeline(
    json_data: Dict[str, Any],
    fsdu_path: str,
    folder_name: str
) -> List[Dict[str, Any]]:
    """
    Main Orchestrator for the Product Placement Flow using Semantic Kernel Services.
    """
    
    logger.info("Starting Product Placement Initial Pipeline ...")
    pipeline_start = time.perf_counter()
    #extract product paths from json data
    product_paths = [
    item["image"]
    for item in json_data
        .get("details", {})
        .get("products", {})
        .get("images", [])
    ]
    
    # Download Assets (Handle Blob URLs)
    logger.info(f"Downloading inputs to local temp... FSDU: {fsdu_path}")
    download_start = time.perf_counter()
    fsdu_local_path = (await download_assets_to_local([fsdu_path]))[0]
    product_local_paths = await download_assets_to_local(product_paths)
    download_end = time.perf_counter()
    download_duration = download_end - download_start
    logger.info(f"Downloaded all assets took {format_duration(download_duration)}")

    # Update variables to use local paths
    fsdu_path = fsdu_local_path
    product_paths = product_local_paths

    # Parse Dimensions
    parse_start = time.perf_counter()
    parsed_data = await parse_placement_data_complete(json_data)
    parse_end = time.perf_counter()
    parse_duration = parse_end - parse_start
    logger.info(f"Parsed placement data took {format_duration(parse_duration)}")
    if "error" in parsed_data:
        logger.error(f"Parsing failed: {parsed_data['error']}")
        return [{"error": parsed_data['error']}]
    blueprint = parsed_data["blueprint"]

    # Annotation Agent
    logger.info("Running Annotation Agent...")
    annotation_start = time.perf_counter()
    annotations = await run_annotation_agent_sk(fsdu_path, product_paths, blueprint)
    annotation_end = time.perf_counter()
    annotation_duration = annotation_end - annotation_start
    logger.info(f"Annotation Agent took {format_duration(annotation_duration)}")
    logger.info(f"Annotation Agent Result: {annotations}")
    if "error" in annotations:
        logger.error(f"Annotation failed: {annotations['error']}")
        return [{"error": annotations['error']}]
    
    # Generate Prompt
    logger.info("Generating Initial Prompt...")
    prompt_start = time.perf_counter()
    fsdu_url = encode_file(fsdu_path)
    product_urls = [encode_file(p) for p in product_paths]
    
    final_prompt = await generate_prompt_sk(annotations, fsdu_url, product_urls)
    prompt_end = time.perf_counter()
    prompt_duration = prompt_end - prompt_start
    logger.info(f"Prompt Generation took {format_duration(prompt_duration)}")
    if final_prompt.startswith("Error"):
        logger.error(final_prompt)
        return [{"error": final_prompt}]
    

    # Retry Logic Loop
    retry_start = time.perf_counter()
    step = "initial"
    attempt = 0
    max_retries = settings.PRODUCT_MAX_RETRY_ATTEMPTS
    threshold = settings.PRODUCT_SCORE_THRESHOLD
    
    best_results = []
    
    while attempt <= max_retries:
        logger.info(f"----- Attempt {attempt + 1} / {max_retries} -----")
        
        # Generate 3 variants in parallel
        tasks_gen = []
        for i in range(3):
            image_start = time.perf_counter()
            tasks_gen.append(generate_composite_image(folder_name, final_prompt, fsdu_path, product_paths, i, attempt, step))
        
        logger.info(f"Prompt used for rendering: {final_prompt}")
        logger.info("Generating 3 variants parallelly...")
        
        generated_paths = await asyncio.gather(*tasks_gen)
        image_end = time.perf_counter()
        image_duration = image_end - image_start
        logger.info(f"Image Generation for 3 variants took {format_duration(image_duration)}")

        # Filter successful generations
        valid_paths = [p for p in generated_paths if not p.startswith("Error")]
        if not valid_paths:
            logger.error("All generations failed.")
            error_msg = (
                generated_paths[0]
                if generated_paths
                else "All generations failed"
            )
            raise RuntimeError(error_msg)

        # Evaluate variants in parallel
        eval_start = time.perf_counter()
        tasks_eval = []
        for p in valid_paths:
            tasks_eval.append(run_critic_sk(final_prompt, fsdu_path, p, product_paths))
            
        logger.info("Evaluating variants parallelly...")
        eval_results = await asyncio.gather(*tasks_eval)
        eval_end = time.perf_counter()
        eval_duration = eval_end - eval_start
        logger.info(f"Evaluation of variants took {format_duration(eval_duration)}")
        
        # Combine results
        current_batch_results = []
        for path, eval_res in zip(valid_paths, eval_results):
            res = {
                "generated_image_path": path,
                "score": eval_res.get("confidence_score", 0),
                "feedback": eval_res.get("feedback", ""),
                "full_eval": eval_res,
                "prompt": final_prompt
            }
            current_batch_results.append(res)
            logger.info(f"Result: {path} -> Score: {res['score']} -> Feedback: {res['feedback']}")

        best_results.extend(current_batch_results)
        
        # Check Success
        passing = [r for r in current_batch_results if r["score"] >= threshold]
        if passing:
            logger.info("Success! Threshold reached.")
            break

        # Refine Prompt if not successful
        if current_batch_results:
             best_candidate = max(current_batch_results, key=lambda x: x.get('score', -1))
             feedback = best_candidate.get('feedback', '')
             if feedback:
                 logger.info("Refining prompt with feedback from best candidate...")
                 final_prompt = f"{final_prompt}\n\nFeedback from previous attempt:\n{feedback}"
        
        attempt += 1
    retry_end = time.perf_counter()
    retry_duration = retry_end - retry_start
    logger.info(f"Retry Loop took {format_duration(retry_duration)}")
        
    unique_results = {r['generated_image_path']: r for r in best_results}.values()
    top3 = sorted(unique_results, key=lambda x: x["score"], reverse=True)[:3]
    final_output = [
        {
            "url": r["generated_image_path"],
            "score": r["score"]
        }
        for r in top3
    ]
    logger.info(f"Returning top {len(final_output)} results from {len(best_results)} total generations.")
    pipeline_end = time.perf_counter()
    duration = pipeline_end - pipeline_start
    logger.info(f"Product Placement Pipeline completed in " f"{format_duration(duration)}")
    return final_output


async def run_product_refinement_pipeline(
    user_feedback: str,
    selected_image_path: str,
    fsdu_path: str,
    json_data: Dict[str, Any],
    folder_name: str
) -> Dict[str, Any]:
    """
    Orchestrates the refinement loop based on User Feedback.
    """
    logger.info("Starting Product Refinement Pipeline...")
    pipeline_start = time.perf_counter()
    #extract product paths from json data
    product_paths = [
    item["image"]
    for item in json_data
        .get("details", {})
        .get("products", {})
        .get("images", [])
    ]
    
    user_feedback = user_feedback + "Keep everything else exactly the same."

    # 0. Download Assets (Ensure local for encoding)
    try:
        download_start = time.perf_counter()
        all_urls = [fsdu_path, selected_image_path] + product_paths
        await download_assets_to_local(all_urls)
        download_end = time.perf_counter()
        download_duration = download_end - download_start
        logger.info(f"Downloaded all assets for refinement took {format_duration(download_duration)}")
    except Exception as e:
        logger.error(f"Failed to download assets: {e}")
        return {"error": f"Asset download failed: {str(e)}"}
    
    # Generate Refinement Prompt
    logger.info("Generating Refinement Prompt...")
    
    try:
        prompt_start = time.perf_counter()
        new_prompt = await generate_product_refinement_plan_sk(
            user_feedback,
            encode_file(selected_image_path), # Current Output
            encode_file(fsdu_path), # Base FSDU
            [encode_file(p) for p in product_paths]
        )
        prompt_end = time.perf_counter()
        prompt_duration = prompt_end - prompt_start
        logger.info(f"Refinement Prompt Generation took {format_duration(prompt_duration)}")
    except Exception as e:
         logger.error(f"Failed to generate refinement prompt: {e}")
         return {"error": f"Refinement prompt generation failed: {str(e)}"}
    
    if new_prompt.startswith("Error"):
        return {"error": new_prompt}
        
    logger.info(f"Refined Prompt: {new_prompt}")
    
    # Build the map of available Semantic Names -> Local Paths
    image_map = {
        "CURRENT_OUTPUT_IMAGE_URL": selected_image_path,
        "BASE_DISPLAY_UNIT_IMAGE_URL": fsdu_path
    }
    
    # Map products dynamically: PRODUCT_A_IMAGE_URL, PRODUCT_B_IMAGE_URL...
    import string
    letters = string.ascii_uppercase
    for idx, path in enumerate(product_paths):
        if idx < len(letters):
            key = f"PRODUCT_{letters[idx]}_IMAGE_URL"
            image_map[key] = path
            
    # Parse the plan using Mapper
    try:
        mapper = ImagePromptMapper()
        mappings = mapper.map_prompt_to_images(new_prompt, image_map)
        
        # Extract ordered paths
        ordered_paths = []
        
        placeholders_in_order = mapper.extract_placeholders(new_prompt)
        for p_name in placeholders_in_order:
            if p_name in mappings:
                 ordered_paths.append(mappings[p_name]['url'])
                 
        if not ordered_paths:
            logger.warning("Mapper found no validity image placeholders. Fallback to default ordering.")
            ordered_paths = [selected_image_path] + product_paths # Fallback strategy
            
        logger.info(f"Refinement Image Inputs Ordered: {placeholders_in_order}")
    except Exception as e:
        logger.error(f"Error in Image Mapper logic: {e}")
        logger.warning("Fallback to default ordering due to mapper error.")
        ordered_paths = [selected_image_path] + product_paths

    # Refinement Loop
    step = "refinement"
    attempt = 0
    max_retries = settings.PRODUCT_REFINE_MAX_RETRY_ATTEMPTS
    
    best_result = None
    
    
    while attempt <= max_retries:
        logger.info(f"----- Refinement Attempt {attempt + 1} -----")
        
        # Generate 3 variants
        tasks_gen = []
        for i in range(3):
            if ordered_paths:
                base_in = ordered_paths[0]
                prods_in = ordered_paths[1:]
            else:
                base_in = selected_image_path
                prods_in = product_paths

            tasks_gen.append(generate_composite_image(folder_name, new_prompt, base_in, prods_in, i, attempt, step))
            
        try:
            generated_paths = await asyncio.gather(*tasks_gen)
            valid_paths = [p for p in generated_paths if not p.startswith("Error")]
        except Exception as e:
             logger.error(f"Error during refinement image generation: {e}")
             valid_paths = []
        
        if not valid_paths:
            logger.error("All refinement generations failed.")
            attempt += 1
            continue
            
        # Evaluate against Feedback
        tasks_eval = []
        evaluate_start = time.perf_counter()
        for p in valid_paths:
            tasks_eval.append(evaluate_product_refinement_result_sk(
                new_prompt, 
                p, # Generated Image
                fsdu_path, # Original Base 
                product_paths # Original Products
            ))
            
        try:
            eval_results = await asyncio.gather(*tasks_eval)
        except Exception as e:
             logger.error(f"Error during refinement evaluation: {e}")
             attempt += 1
             continue
        evaluate_end = time.perf_counter()
        evaluate_duration = evaluate_end - evaluate_start
        logger.info(f"evaluation task took {format_duration(evaluate_duration)}")
        candidates = []
        for path, res in zip(valid_paths, eval_results):
            c = {
                "generated_image_path": path,
                "score": res.get("confidence_score", 0),
                "feedback": res.get("feedback", ""),
                "prompt": new_prompt
            }
            candidates.append(c)
            logger.info(f"Refinement Candidate: {path} -> Score: {c['score']}")
            
        if not candidates:
            attempt += 1
            continue
            
        # Pick best of this batch
        batch_best = max(candidates, key=lambda x: x['score'])
        
        # Track global best
        if best_result is None or batch_best['score'] > best_result['score']:
            best_result = batch_best
            
        # Threshold Check
        if batch_best['score'] >= settings.PRODUCT_REFINE_SCORE_THRESHOLD:
            logger.info("Refinement Threshold Reached!")
            pipeline_end = time.perf_counter()
            duration = pipeline_end - pipeline_start
            logger.info(f"Product Refinement Pipeline completed in " f"{format_duration(duration)}")
            return {
                "url": batch_best["generated_image_path"],
                "score": batch_best["score"]
            }
            
        # If not reached, refine the prompt using the Edit Patch Agent
        if attempt < max_retries:
             logger.info("Generating Patched Prompt for Refinement using Edit Patch Agent...")
             
             # The existing feedback gathered from the evaluation step
             eval_result_json = {
                 "confidence_score": batch_best.get('score', 0),
                 "feedback": batch_best.get('feedback', [])
             }
             
             try:
                 new_prompt = await generate_patch_refinement_plan_sk(
                     original_prompt=new_prompt, # Use the current iteration's prompt
                     evaluation_result_json=eval_result_json
                 )
                 logger.info(f"Patched Refinement Prompt: {new_prompt}")
             except Exception as e:
                 logger.error(f"Patch agent failed: {e}")

        attempt += 1
        
    logger.info("Max retries reached. Returning best result found.")
    #return best_result or {"error": "Refinement failed to produce valid results"}
    pipeline_end = time.perf_counter()
    duration = pipeline_end - pipeline_start
    logger.info(f"Product Refinement Pipeline completed in " f"{format_duration(duration)}")
    return (
        {
           "url": best_result.get("generated_image_path"),
           "score": best_result.get("score")
        }
        if best_result
        else {"error": "Refinement failed to produce valid results"}
    )
