import asyncio
import os
import json
from .logger import get_logger
from .storage import BlobManager
from .services import (
    get_image_client,
    generate_layout_annotations_robust,
    parse_annotations_to_string,
    generate_graphics_prompt,
    render_single_variant,
    evaluate_variants_with_critic,
    apply_critic_to_prompt,
    generate_refinement_plan,
    evaluate_refinement_result,
    ImagePromptMapper,
    run_architecture_analyzer
)
from .utils import encode_bytes_to_base64, make_output_filename
from .config import config
from app.core.config import settings
from app.ai.product.pipelines import format_duration
import time

logger = get_logger("Graphics_Pipeline")

async def run_graphics_initial_pipeline(
    folder_name: str,
    base_shelf_url: str,
    header_url: str = None,
    side_url: str = None,
    front_lip_url: str = None,
    plinth_url: str = None
):
    """
    Main entry point for the graphics generation pipeline using URLs (blob or local).
    """
    pipeline_start = time.perf_counter()
    blob_manager = BlobManager()
    image_client = get_image_client()

    try:
        # 1. Gather active assets
        active_assets_urls = {
            "Base_Shelf_Structure": base_shelf_url,
            "Header_Graphic": header_url,
            "Left_Side_Panel_Graphic": side_url,
            "Front_Lip_Graphic": front_lip_url,
            "Base_Plinth_Graphic": plinth_url,
        }
        # Filter None
        active_assets_urls = {k: v for k, v in active_assets_urls.items() if v is not None}

        if "Base_Shelf_Structure" not in active_assets_urls:
             raise ValueError("Base shelf image is mandatory.")

        graphic_keys = [k for k in active_assets_urls if k != "Base_Shelf_Structure"]

        # 2. Download all assets to bytes (parallel)
        logger.info("Downloading assets...")
        download_start = time.perf_counter()
        async def fetch(key, url):
            data = await blob_manager.download_image_to_bytes(url)
            return key, data

        tasks = [fetch(k, v) for k, v in active_assets_urls.items()]
        results = await asyncio.gather(*tasks)
        asset_data_map = dict(results) # {key: bytes}
        download_end = time.perf_counter()
        download_duration = download_end - download_start
        logger.info(f"Downloaded assets in {format_duration(download_duration)}")

        # 3. Architecture Analysis (Dynamic Region Specs)
        logger.info("Running Architecture Analyzer...")
        architect_start = time.perf_counter()
        base_shelf_bytes = asset_data_map["Base_Shelf_Structure"]
        dynamic_specs = await run_architecture_analyzer(base_shelf_bytes)
        logger.info(f"Dynamic Specs:\n{json.dumps(dynamic_specs, indent=2)}")
        architect_end = time.perf_counter()
        architect_duration = architect_end - architect_start
        logger.info(f"Architecture analysis completed in {format_duration(architect_duration)}")

        # 4. Semantic pipeline (annotation → instructions → theme prompt)
        logger.info("Generating annotations...")
        annotation_start = time.perf_counter()
        annotation_json = await generate_layout_annotations_robust(
            graphic_keys, 
            asset_data_map, 
            base_shelf_bytes,
            region_specs=dynamic_specs
        )
        
        instructions = parse_annotations_to_string(annotation_json)
        
        encoded_list = [encode_bytes_to_base64(asset_data_map["Base_Shelf_Structure"])]
        encoded_list += [encode_bytes_to_base64(asset_data_map[k]) for k in graphic_keys]
        annotation_end = time.perf_counter()
        annotation_duration = annotation_end - annotation_start
        logger.info(f"Annotations generated in {format_duration(annotation_duration)}")

        logger.info("Generating theme prompt...")
        prompt_start = time.perf_counter()
        current_prompt = await generate_graphics_prompt(instructions, encoded_list)
        logger.info(f"Initial Prompt:\n{current_prompt}")
        prompt_end = time.perf_counter()
        prompt_duration = prompt_end - prompt_start
        logger.info(f"Prompt generated in {format_duration(prompt_duration)}")

        # 4. Prepare images for rendering (list of tuples for AzureOpenAI SDK)
        images_for_render = [
            ("base_shelf.png", asset_data_map["Base_Shelf_Structure"])
        ] + [
            (f"{k}.png", asset_data_map[k])
            for k in graphic_keys
        ]

        # Helper to calculate filenames
        base_shelf_filename = os.path.basename(base_shelf_url) if base_shelf_url else "base_shelf.png"

        render_start = time.perf_counter()
        async def render_three(step_name, prompt):
            tasks = []
            for i in range(1, 4):
                fname = make_output_filename(step_name, base_shelf_filename, i)
                blob_path = f"project/{folder_name}/{fname}"
                tasks.append(render_single_variant(image_client, images_for_render, prompt, blob_manager, blob_path))
            
            # results: list of (url, bytes)
            results = await asyncio.gather(*tasks)
            return [{"url": r[0], "bytes": r[1]} for r in results]

        logger.info("-----Initial Renders phase started-----")
        # 5. Initial Renders
        current_variants = await render_three("initial", current_prompt)
        render_end = time.perf_counter()
        render_duration = render_end - render_start
        logger.info(f"Initial renders completed in {format_duration(render_duration)}")
        # 6. Critic Loop
        attempt = 0
        refined_prompt = current_prompt
        
        all_critic_results = []

        while True:
            logger.info(f"-----Critic Evaluation - Attempt {attempt} started-----")
            eval_start = time.perf_counter()
            critic_results = await evaluate_variants_with_critic(
                variant_results=current_variants,
                user_prompt=refined_prompt,
                base_img_bytes=asset_data_map["Base_Shelf_Structure"],
                graphic_asset_bytes_list=[asset_data_map[k] for k in graphic_keys],
                client=image_client
            )

            for r in critic_results:
                logger.info(f"{r['url']} : {r['overall_score']:.2f} | {r['feedback']}")

            all_critic_results.extend(critic_results)
            eval_end = time.perf_counter()
            eval_duration = eval_end - eval_start
            logger.info(f"Critic evaluation completed in {format_duration(eval_duration)}")
            # Success check
            passing = [r for r in critic_results if r["overall_score"] >= settings.GRAPHIC_SCORE_THRESHOLD]
            if passing:
                 # Deduplicate by URL to ensure uniqueness
                 unique_results = {r['url']: r for r in all_critic_results}.values()
                 top3 = sorted(unique_results, key=lambda r: r["overall_score"], reverse=True)[:3]
                 logger.info(f"SUCCESS! Threshold reached. Returning top {len(top3)} results.")
                 pipeline_end = time.perf_counter()
                 pipeline_duration = pipeline_end - pipeline_start
                 logger.info(f"Graphics Pipeline completed in {format_duration(pipeline_duration)}")
                 return [{"url": t["url"], "score": round(t["overall_score"])} for t in top3]
            
            # Retry Limit
            if attempt >= settings.GRAPHIC_MAX_RETRY_ATTEMPTS:
                logger.warning("Max retries reached.")
                # Return top 3 from all
                unique_results = {r['url']: r for r in all_critic_results}.values()
                top3 = sorted(unique_results, key=lambda r: r["overall_score"], reverse=True)[:3]
                pipeline_end = time.perf_counter()
                pipeline_duration = pipeline_end - pipeline_start
                logger.info(f"Graphics Pipeline completed in {format_duration(pipeline_duration)}")
                return [{"url": t["url"], "score": round(t["overall_score"])} for t in top3]

            # Refine
            best_candidate = max(critic_results, key=lambda r: r["overall_score"])
            logger.info(f"Refining based on: {best_candidate['url']}")
            refined_prompt = apply_critic_to_prompt(refined_prompt, best_candidate["critique"])
            
            current_variants = await render_three(f"retry_{attempt+1}", refined_prompt)
            attempt += 1

    except Exception as e:
        logger.exception("Graphics Pipeline Failed")
        raise e


async def run_graphics_refinement_pipeline(
    folder_name: str,
    user_feedback: str,
    selected_output_url: str,
    base_shelf_url: str,
    header_url: str = None,
    side_url: str = None,
    front_lip_url: str = None,
    plinth_url: str = None
):
    """
    Refinement pipeline: Orchestrator -> Render -> Evaluate -> Loop
    """
    logger.info("Starting User Refinement Pipeline...")
    pipeline_start = time.perf_counter()
    blob_manager = BlobManager()
    image_client = get_image_client()

    # Construct list of graphic assets from named arguments
    graphic_assets_urls = [u for u in [header_url, side_url, front_lip_url, plinth_url] if u]

    try:
        # 1. Download all assets to bytes
        download_start = time.perf_counter()
        async def fetch(url):
            if not url: return None
            return await blob_manager.download_image_to_bytes(url)

        base_bytes = await fetch(base_shelf_url)
        output_bytes = await fetch(selected_output_url)
        asset_bytes_list = []
        for url in graphic_assets_urls:
            b = await fetch(url)
            if b: asset_bytes_list.append(b)
            
        if not base_bytes or not output_bytes:
            raise ValueError("Base shelf and Output image are required.")
        download_end = time.perf_counter()
        download_duration = download_end - download_start
        logger.info(f"Downloaded assets in {format_duration(download_duration)}")

        # 2. Refinement Loop
        attempt = 0
        current_output_bytes = output_bytes 
        current_output_url_internal = selected_output_url
        
        # Track initial user feedback to append constraints
        current_feedback = user_feedback 
        all_candidates_across_attempts = []
        logger.info(f"Refinement Attempt {attempt+1}")
        
        # A. Orchestrator Plan
        prompt_start = time.perf_counter()
        prompt = await generate_refinement_plan(
            current_feedback,
            base_bytes,
            current_output_bytes,
            asset_bytes_list
        )
        
        logger.info(f"Prompt: {prompt}")
        prompt_end = time.perf_counter()
        prompt_duration = prompt_end - prompt_start
        logger.info(f"Refinement prompt generated in {format_duration(prompt_duration)}")

        image_registry = {
            "header": header_url,
            "side": side_url,
            "rails": front_lip_url,
            "plinth": plinth_url,
            "base_display_unit_url": base_shelf_url,
            "output_image_url": selected_output_url, 
        }

        graphic_assets_urls = [
            v for k, v in image_registry.items()
            if v and k not in ("base_display_unit_url", "output_image_url")
        ]

        mapper = ImagePromptMapper()
        mappings = mapper.map_prompt_to_images(prompt, image_registry)
        #path = []

        # Prepare images for rendering as (filename, bytes) tuples
        images_for_render = []
        input_files = [] 
        
        for placeholder, info in mappings.items():
            if info['file_path']:
                url = info['file_path']
                var_name = info['matched_variable'] or "image"
                
                logger.info(f"{placeholder} -> {var_name}")
                logger.info(f"  Path: {url}\n")
                input_files.append(url)
                
                # Fetch bytes and append to list
                b = await fetch(url)
                if b:
                    # Extract extension from url or default to .png
                    ext = os.path.splitext(url)[1] 
                    if not ext: ext = ".png"
                    fname = f"{var_name}{ext}"
                    images_for_render.append((fname, b))

        logger.info(f"Rendering 3 variants with inputs: {input_files}")
        base_prompt = prompt
        current_feedback = base_prompt

        while attempt <= settings.GRAPHIC_REFINE_MAX_RETRY_ATTEMPTS:
            logger.info(f"Refinement Loop Iteration {attempt+1}")
            step_name = f"refine_{attempt+1}"
            render_start = time.perf_counter()
            async def render_three_refinements():
                tasks = []
                logger.info(f"Prompt used for rendering: {current_feedback}") 
                logger.info(f"Rendering 3 variants with inputs: {input_files}")
                        
                for i in range(1, 4):
                    fname = make_output_filename(step_name, "refinement.png", i)
                    blob_path = f"project/{folder_name}/{fname}"
                    tasks.append(render_single_variant(
                        image_client, 
                        images_for_render, 
                        current_feedback, 
                        blob_manager, 
                        blob_path
                    ))
                return await asyncio.gather(*tasks)
            
            # variants: list of (url, bytes)
            variants = await render_three_refinements()
            render_end = time.perf_counter()
            render_duration = render_end - render_start 
            logger.info(f"Rendered 3 variants in {format_duration(render_duration)}")
            
            # D. Evaluate All Variants
            logger.info("-----Evaluating all 3 variants-----")
            eval_start = time.perf_counter()
            async def eval_variant(v_url, v_bytes):
                res = await evaluate_refinement_result(
                    output_bytes,
                    v_bytes,
                    current_feedback,
                    image_client
                )
                return {
                    "url": v_url,
                    "bytes": v_bytes,
                    "score": res.get("confidence_score", 0),
                    "feedback": res.get("feedback", [])
                }

            eval_tasks = [eval_variant(v[0], v[1]) for v in variants]
            candidates = await asyncio.gather(*eval_tasks)
            eval_end = time.perf_counter()
            eval_duration = eval_end - eval_start
            logger.info(f"Evaluation completed in {format_duration(eval_duration)}")
            # Track globally
            all_candidates_across_attempts.extend(candidates)
            
            # Log results
            for c in candidates:
                logger.info(f"{c['url']} : {c['score']:.2f} | {c['feedback']}")

            # Pick Best
            best_candidate = max(candidates, key=lambda x: x['score'])
            logger.info(f"Best Candidate: {best_candidate['url']} (Score: {best_candidate['score']})")

            score = best_candidate["score"]
            feedback = best_candidate["feedback"]
            
            # Use threshold from config or default 75
            threshold = settings.GRAPHIC_REFINE_SCORE_THRESHOLD

            if score >= threshold:
                 logger.info("Refinement Successful!")
                 pipeline_end = time.perf_counter()
                 pipeline_duration = pipeline_end - pipeline_start
                 logger.info(f"Pipeline completed in {format_duration(pipeline_duration)}")
                 return {"url": best_candidate["url"], "score": round(score)}
                 
            # E. Prepare for next loop
            feedback_str = "\n".join(feedback)
            regeneration_block = f"""--- REGENERATION ATTEMPT - DELTA CORRECTIONS:
                The previous rendering attempt(s) were evaluated and the following specific issues were identified:
                {feedback_str}
                
                INSTRUCTION: Apply ONLY these corrections while keeping everything else from the base requirements unchanged.
                Do not reinterpret the base prompt - simply fix the identified issues.
                """
            current_feedback = base_prompt + "\n\n" + regeneration_block
            
            # Use the best candidate as the base for the next iteration
            current_output_bytes = best_candidate["bytes"]
            current_output_url_internal = best_candidate["url"]
            attempt += 1
            logger.info(f"Preparing for next attempt {attempt+1} with updated feedback.")
            
        logger.warning("Max refinement retries reached.")

        # Picking global best from all attempts
        start=time.perf_counter()
        if all_candidates_across_attempts:
            global_best = max(all_candidates_across_attempts, key=lambda x: x['score'])
            logger.info(f"Returning GLOBAL BEST candidate from all attempts: {global_best['url']} (Score: {global_best['score']})")
            return {
                "url": global_best["url"], 
                "score": round(global_best["score"])
            }
        end = time.perf_counter()
        logger.info(f"Global best selection took {format_duration(end - start)}")
        return {"url": current_output_url_internal, "score": round(score)}

    except Exception as e:
        logger.exception("Refinement Pipeline Failed")
        raise e