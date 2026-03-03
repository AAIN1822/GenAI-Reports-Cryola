import re
import asyncio
from openai import AzureOpenAI
from semantic_kernel.contents import ChatMessageContent, TextContent, ImageContent
from app.core.config import settings
from .logger import get_logger
from .storage import BlobManager, encode_bytes_to_base64
from .models import FeedbackAnalyzerOutput, RefinementEvaluationResult
from .prompts import theme_prompt, create_updated_prompt
from .services import (
    render_single_variant_theme,
    render_opencv_in_memory, 
    create_evaluator,
    evaluate_single_image,
    create_feedback_analyzer,
    create_refinement_evaluator,
    pick_best_line_color
)
import time
from app.ai.product.pipelines import format_duration
from app.utils.zoomed_canvas import create_zoomed_canvas

# ==========================================
# 1. INITIAL GENERATION
# ==========================================

async def run_theme_initial(client: AzureOpenAI, input_blob_url: str, hex_code: str, folder_name: str):
    logger = get_logger("ThemeEngine_Pipelines")
    pipeline_start = time.perf_counter()
    try:
        """
        Formerly run_initial_generation
        """
        storage = BlobManager()
        logger.info(f"--- PHASE 1: GENERATION ({input_blob_url}) ---")
        
        download_start = time.perf_counter()
        source_bytes = await storage.download_image_to_bytes(input_blob_url)
        zoomed_bytes = create_zoomed_canvas(source_bytes)
        download_end = time.perf_counter()
        download_duration = download_end - download_start
        logger.info(f"Downloaded source image in {format_duration(download_duration)}")
        
        
        # Determine shared line color
        bgr_color = tuple(int(hex_code.lstrip('#')[i:i+2], 16) for i in (4, 2, 0))
        line_color = pick_best_line_color(bgr_color)
        base_prompt = theme_prompt(hex_code, line_color)
        
        # 1. Render All
        # Parallelize GPT calls
        render_start = time.perf_counter()
        tasks = [
            render_single_variant_theme(client, zoomed_bytes, base_prompt, folder_name, "initial", i, line_color) 
            for i in range(1, 3) 
        ]
        results = await asyncio.gather(*tasks)
        gpt_urls = [r for r in results if r]
        render_end = time.perf_counter()
        render_duration = render_end - render_start
        logger.info(f"Rendered GPT images in {format_duration(render_duration)}")

        # OpenCV Render
        opencv_start = time.perf_counter()
        opencv_url = render_opencv_in_memory(zoomed_bytes, hex_code, folder_name, line_color)
        opencv_end = time.perf_counter()
        opencv_duration = opencv_end - opencv_start
        logger.info(f"Rendered OpenCV image in {format_duration(opencv_duration)}")
        all_img_meta = []
        for i, url in enumerate(gpt_urls, 1): all_img_meta.append({"id": f"v{i}", "url": url, "method": "gpt"})
        if opencv_url: all_img_meta.append({"id": f"v{len(gpt_urls)+1}", "url": opencv_url, "method": "opencv"})
        
        if not all_img_meta: return []

        # --- LOGGING : Evaluation  ---
        logger.info("Evaluating Initial Images (Parallel)")
                
        # 2. Evaluate All (Parallel)
        evaluation_start = time.perf_counter()
        evaluator = create_evaluator()
        
        eval_tasks = [
            evaluate_single_image(evaluator, zoomed_bytes, m['url'], hex_code, base_prompt, m['id'])
            for m in all_img_meta
        ]
        eval_results_list = await asyncio.gather(*eval_tasks)
        evaluation_end = time.perf_counter()
        evaluation_duration = evaluation_end - evaluation_start
        logger.info(f"Evaluated images in {format_duration(evaluation_duration)}")
        # 3. Map Results
        results = []
        for i, res in enumerate(eval_results_list):
            meta = all_img_meta[i]
            score = res['score']
            feedback = res['feedback']
            
            # --- LOGGING: URL, SCORE & FEEDBACK ---
            logger.info(f"RESULT [{meta['id']}] | Score: {score} | URL: {meta['url']} | Feedback : {feedback}")
            
            results.append({
                "id": meta['id'],
                "url": meta['url'],
                "score": score,
                "passed": score >= settings.THEME_SCORE_THRESHOLD,
                "method": meta['method'],
                "feedback": feedback
            })

        # 4. Auto-Regen Loop
        passed = [r for r in results if r['passed']]
        attempt = 1
        
        while not passed and attempt <= settings.THEME_MAX_RETRY_ATTEMPTS:
            retry_start = time.perf_counter()
            logger.info(f"--- PHASE 2: AUTO-REGEN (Attempt {attempt}) ---")
            
            # Get feedback from best failed GPT
            gpt_fails = [r for r in results if r['method'] == 'gpt']
            best_fail = max(gpt_fails, key=lambda x: x['score']) if gpt_fails else None
            feedback_agg = best_fail['feedback'] if best_fail else "Improve structure."
            
            updated_prompt = create_updated_prompt(base_prompt, feedback_agg)

            # --- LOGGING: AGGREGATED PROMPT ---
            logger.info(f"REGEN PROMPT (Attempt {attempt}):\n{updated_prompt}")
            
            # Parallelize Retry calls
            retry_tasks = [
                render_single_variant_theme(client, zoomed_bytes, updated_prompt, folder_name, f"regen_v{attempt}", i, line_color)
                for i in range(1, 4)
            ]
            retry_results = await asyncio.gather(*retry_tasks)
            retry_urls = [r for r in retry_results if r]
            
            retry_img_meta = []
            for i, url in enumerate(retry_urls, 1): retry_img_meta.append({"id": f"v{i}", "url": url, "method": "gpt"})
            
            if not retry_img_meta: return []

            # --- LOGGING : Evaluation  ---
            logger.info("Evaluating Initial Retry Images (Parallel)")
                
            if retry_urls:
                retry_eval_tasks = [
                    evaluate_single_image(evaluator, zoomed_bytes, m['url'], hex_code, updated_prompt, m['id'])
                    for m in retry_img_meta
                ]
                retry_eval_list = await asyncio.gather(*retry_eval_tasks)
                
                # Map new results
                for i, res in enumerate(retry_eval_list):
                    meta = retry_img_meta[i]
                    score = res['score']
                    feedback = res['feedback']

                    # --- LOGGING ADDED: URL, SCORE & FEEDBACK ---
                    logger.info(f"RESULT [{meta['id']}] | Score: {score} | URL: {meta['url']} | Feedback : {feedback}")


                    results.append({
                        "id": f"r{attempt}_v{i+1}",
                        "url": meta['url'],
                        "score": score,
                        "passed": score >= settings.THEME_SCORE_THRESHOLD,
                        "method": "gpt",
                        "feedback": feedback
                    })
            
            passed = [r for r in results if r['passed']]
            attempt += 1
            retry_end = time.perf_counter()
            retry_duration = retry_end - retry_start
            logger.info(f"Auto-regen attempt {attempt-1} finished in {format_duration(retry_duration)}")
            
        # Return only the last 3 results (most recent images), in correct order
        last_three = results[-3:] if len(results) >= 3 else results
        pipeline_end = time.perf_counter()
        pipeline_duration = pipeline_end - pipeline_start
        logger.info(f"theme pipeline finished in {format_duration(pipeline_duration)}")
        return [
            {
                "url": r["url"],
                "score": round(r["score"])
            }
            for r in last_three
        ]
    
    except Exception as e:
        logger.exception(f"run_theme_initial FAILED: {str(e)}")
        return {
            "status": "error",
            "message": "Theme Initial Pipeline Failed",
            "error": str(e),
            "fallback_results": []
        }

# ==========================================
# 2. REFINEMENT 
# ==========================================

async def run_theme_refinement(client: AzureOpenAI, chosen_url: str, feedback: str, folder_name:str):
    logger = get_logger("ThemeEngine_Pipelines")
    pipeline_start = time.perf_counter()
    try:    
        """
        Formerly run_refinement_pipeline
        """
        
        feedback = feedback + "Do not modify any other part of the display unit. Keep all structure, shapes, outlines, colors, and proportions the exactly same."
        logger.info("--- PHASE 3: REFINEMENT PIPELINE ---")

        # --- LOGGING: USER CHOICE & FEEDBACK ---
        logger.info(f"User Selected Image: {chosen_url}")
        logger.info(f"User Feedback: {feedback}")

        storage = BlobManager()
        
        # 1. Analyze Feedback
        download_start = time.perf_counter()
        analyzer = create_feedback_analyzer()
        chosen_bytes = await storage.download_image_to_bytes(chosen_url)
        download_end = time.perf_counter()
        download_duration = download_end - download_start
        logger.info(f"Downloaded chosen image in {format_duration(download_duration)}")
        prompt_start = time.perf_counter()
        msg_items = [ImageContent(uri=encode_bytes_to_base64(chosen_bytes)), TextContent(text=f"User feedback: {feedback}")]
        resp_text = ""
        async for resp in analyzer.invoke([ChatMessageContent(role="user", items=msg_items)]): resp_text += str(resp.content)
        
        try:
            cleaned = re.sub(r'```json\s*|\s*```', '', resp_text)
            match = re.search(r'\{.*\}', cleaned, re.DOTALL)
            refined_prompt = FeedbackAnalyzerOutput.model_validate_json(match.group()).refined_prompt
        except:
            refined_prompt = f"Apply changes: {feedback}"

        # --- LOGGING : REFINED PROMPT ---
        prompt_end = time.perf_counter()
        prompt_duration = prompt_end - prompt_start
        logger.info(f"Analyzed feedback and generated refined prompt in {format_duration(prompt_duration)}")
        logger.info(f"Generated Refined Prompt:\n{refined_prompt}")

        # 2. Render V1
        render_start = time.perf_counter()
        final_url = await render_single_variant_theme(client, chosen_bytes, refined_prompt, folder_name, "refinement_v1", 1)
        final_urls = [final_url] if final_url else []
        render_end = time.perf_counter()
        render_duration = render_end - render_start
        logger.info(f"Rendered Refinement V1 image in {format_duration(render_duration)}")
        if not final_urls: return None
        best_url = final_urls[0]
        
        # --- LOGGING : Evaluation---
        logger.info("Evaluating Refinement Image")

        # 3. Evaluate V1
        eval_start = time.perf_counter()
        ref_evaluator = create_refinement_evaluator()
        best_bytes = await storage.download_image_to_bytes(best_url)
        eval_end = time.perf_counter()
        eval_duration = eval_end - eval_start
        logger.info(f"Downloaded refinement image in {format_duration(eval_duration)}")
        
        evaluation_start = time.perf_counter()
        eval_msg = ChatMessageContent(role="user", items=[
            ImageContent(uri=encode_bytes_to_base64(chosen_bytes)), 
            TextContent(text=f"Refined Prompt: {refined_prompt}"),
            ImageContent(uri=encode_bytes_to_base64(best_bytes))
        ])
        
        eval_resp = ""
        async for resp in ref_evaluator.invoke([eval_msg]): eval_resp += str(resp.content)
        
        score = 0
        expl = ""
        try:
            cleaned = re.sub(r'```json\s*|\s*```', '', eval_resp)
            match = re.search(r'\{.*\}', cleaned, re.DOTALL)
            if match:
                res = RefinementEvaluationResult.model_validate_json(match.group())
                score = res.confidence_score
                expl = res.explanation
        except: pass
        
        best_eval_text = eval_resp
        best_score = score
        evaluation_end = time.perf_counter()
        evaluation_duration = evaluation_end - evaluation_start
        logger.info(f"Evaluated refinement image in {format_duration(evaluation_duration)}")

        # --- LOGGING: REFINEMENT SCORE ---
        logger.info(f"Refinement V1 Score: {score} | URL: {best_url} | Feedback : {expl}")

        # 4. RETRY LOGIC
        if score < settings.THEME_REFINE_SCORE_THRESHOLD:
            retry_start = time.perf_counter()
            logger.info(f"Score {score} < {settings.THEME_REFINE_SCORE_THRESHOLD}. Retrying...")
            retry_prompt = create_updated_prompt(refined_prompt, expl) # Delta Correction
            logger.info(f"Refinement Retry Prompt:\n{retry_prompt}")
            
            retry_url = await render_single_variant_theme(client, chosen_bytes, retry_prompt, folder_name, "refinement_retry", 1)
            retry_urls = [retry_url] if retry_url else []
            
            if retry_urls:
                retry_url = retry_urls[0]
                retry_bytes = await storage.download_image_to_bytes(retry_url)

                # --- LOGGING : Evaluation  ---
                logger.info("Evaluating Refinement Retry Image")
                
                # Evaluate V2
                eval_msg_2 = ChatMessageContent(role="user", items=[
                    ImageContent(uri=encode_bytes_to_base64(chosen_bytes)), 
                    TextContent(text=f"Refined Prompt: {refined_prompt}"),
                    ImageContent(uri=encode_bytes_to_base64(retry_bytes))
                ])
                eval_resp_2 = ""
                async for resp in ref_evaluator.invoke([eval_msg_2]): eval_resp_2 += str(resp.content)
                
                score_2 = 0
                try:
                    cleaned = re.sub(r'```json\s*|\s*```', '', eval_resp_2)
                    match = re.search(r'\{.*\}', cleaned, re.DOTALL)
                    if match: score_2 = RefinementEvaluationResult.model_validate_json(match.group()).confidence_score
                except: pass
                
                if score_2 > score:
                    logger.info(f"Retry improved ({score_2} > {score}). Keeping V2 with URL : {retry_url}")
                    best_url = retry_url
                    best_score = score_2
                else:
                    logger.info(f"Retry did not improve. Keeping V1 with URL : {best_url} | Score : {score}.")
            retry_end = time.perf_counter()
            retry_duration = retry_end - retry_start
            logger.info(f"Refinement retry finished in {format_duration(retry_duration)}")

        pipeline_end = time.perf_counter()
        pipeline_duration = pipeline_end - pipeline_start
        logger.info(f"theme refinement pipeline finished in {format_duration(pipeline_duration)}")
        return {"url": best_url, "score" : round(best_score)}
    
    except Exception as e:
        logger.exception(f"run_theme_refinement FAILED: {str(e)}")
        return {
            "status": "error",
            "message": "Theme Refinement Pipeline Failed",
            "error": str(e),
            "fallback_result": None
        }