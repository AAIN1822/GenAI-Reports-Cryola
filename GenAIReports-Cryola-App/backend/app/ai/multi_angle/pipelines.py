
import asyncio, time
from typing import Dict, List, Any
from app.ai.multi_angle.logger import get_logger
from app.ai.product.pipelines import format_duration
from app.ai.multi_angle.services import (
    generate_image_azure,
    evaluate_l2r_image_sk,
    evaluate_straight_view_image_sk
)
from app.ai.multi_angle.multi_angle_prompts import (
    STRAIGHT_VIEW_PROMPT_CONSTRUCTOR_SYSTEM_PROMPT,
    L2R_PROMPT_WITHOUT_SP,
    L2R_PROMPT_WITH_SP)
from app.core.config import settings
logger = get_logger("MultiAngle_Pipeline")

async def run_multi_angle_pipeline(
    json_data: Dict[str, Any],
    input_image_path: str,
    folder_name: str
) -> List[Dict[str, Any]]:
    """
    Orchestrates the multi-angle generation pipeline.
    
    1. Generates Edit Prompt (using L2R logic).
    2. Generates 3 L2R images and 3 Straight View images concurrently.
    3. Evaluates all generated images concurrently using respective critics.
    4. Aggregates and returns results.
    """
    logger.info("Starting Multi-Angle Pipeline...")
    pipeline_start = time.perf_counter()
    # Logic to determine user prompt depending on whether sidepanel is present or not
    sidepanel_image = json_data.get("details", {}).get("sidepanel", {}).get("image", "")
    has_valid_sidepanel = bool(sidepanel_image and sidepanel_image.strip())
    logger.info(f"Has valid sidepanel: {has_valid_sidepanel}")
    
    l2r_prompt = L2R_PROMPT_WITH_SP if has_valid_sidepanel else L2R_PROMPT_WITHOUT_SP
    attempt = 0
    
    # Track completion
    l2r_done = False
    straight_done = False
    
    # Store best results across attempts
    final_l2r_results = []
    final_straight_results = []
    
    # Current prompts (start with initial)
    current_l2r_prompt = l2r_prompt
    current_straight_prompt = STRAIGHT_VIEW_PROMPT_CONSTRUCTOR_SYSTEM_PROMPT
    
    while attempt <= settings.MULTI_ANGLE_MAX_RETRY:
        logger.info(f"--- Iteration {attempt + 1} (Max: {settings.MULTI_ANGLE_MAX_RETRY + 1}) ---")
        
        # Define tasks locally to avoid stale objects
        l2r_tasks = []
        straight_tasks = []
        
        # Only queue if not done
        if not l2r_done:
            logger.info(f"Queueing L2R Generation using prompt : {current_l2r_prompt}...")
            l2r_tasks = [
                generate_image_azure(folder_name, current_l2r_prompt, input_image_path, f"multi_angle_Left2Right_attempt_{attempt}", i) 
                for i in range(1,4)
            ]
            
        if not straight_done:
            logger.info(f"Queueing Straight View Generation using prompt : {current_straight_prompt}...")
            straight_tasks = [
                generate_image_azure(folder_name, current_straight_prompt, input_image_path, f"multi_angle_straight_view_attempt_{attempt}", i)
                for i in range(1,4)
            ]
        
        if not l2r_tasks and not straight_tasks:
            logger.info("All views satisfy thresholds. Stopping early.")
            break
            
        # Execute groups
        try:
            execute_start = time.perf_counter()
            l2r_paths, straight_paths = await asyncio.gather(
                asyncio.gather(*l2r_tasks),
                asyncio.gather(*straight_tasks)
            )
            execute_end = time.perf_counter()
            execute_duration = execute_end - execute_start
            logger.info(f"Generation tasks completed in {format_duration(execute_duration)}")
        except Exception as e:
            logger.error(f"Error during parallel generation: {e}")
            l2r_paths, straight_paths = [], []
        
        valid_l2r = [p for p in l2r_paths if p is not None]
        valid_straight = [p for p in straight_paths if p is not None]
        
        logger.info(f"Generated {len(valid_l2r)} L2R images and {len(valid_straight)} Straight View images.")

        # Parallel Evaluation
        eval_tasks_l2r = []
        eval_tasks_straight = []
        
        # L2R Evaluations
        l2r_eval_start = time.perf_counter()
        for path in valid_l2r:
            eval_tasks_l2r.append(evaluate_l2r_image_sk(path, input_image_path, current_l2r_prompt))
        l2r_eval_end = time.perf_counter()
        l2r_eval_duration = l2r_eval_end - l2r_eval_start
        logger.info(f"L2R evaluation tasks in {format_duration(l2r_eval_duration)}")
            
        # Straight View Evaluations
        straight_eval_start = time.perf_counter()
        for path in valid_straight:
            eval_tasks_straight.append(evaluate_straight_view_image_sk(path, input_image_path, current_straight_prompt))
        straight_eval_end = time.perf_counter()
        straight_eval_duration = straight_eval_end - straight_eval_start
        logger.info(f"Straight evaluation tasks in {format_duration(straight_eval_duration)}")
            
        # Run evaluations parallelly
        try:
            eval_start = time.perf_counter()
            l2r_results, straight_results = await asyncio.gather(
                asyncio.gather(*eval_tasks_l2r),
                asyncio.gather(*eval_tasks_straight)
            )
            eval_end = time.perf_counter()
            eval_duration = eval_end - eval_start
            logger.info(f"Evaluation tasks completed in {format_duration(eval_duration)}")
        except Exception as e:
            logger.error(f"Error during parallel evaluation: {e}")
            l2r_results, straight_results = [], []
        
        # Log & Process L2R
        if not l2r_done and l2r_results:
            logger.info("=== L2R Results (Current Iteration) ===")
            for res in l2r_results:
                logger.info(f"Score: {res.get('score', 0)} | Path: {res.get('output_path', '')} | Feedback: {res.get('feedback', '')}")
            
            # Helper to safely get score
            def get_score(item):
                val = item.get('score', 0)
                try: 
                    return float(val) if val is not None else 0
                except: return 0

            best_l2r_current = sorted(l2r_results, key=get_score, reverse=True)[0]
            current_score = get_score(best_l2r_current)
            
            # Check threshold
            if current_score >= settings.MULTI_ANGLE_L2R_VIEW_THRESHOLD:
                logger.info(f"L2R Passed Threshold ({current_score} >= {settings.MULTI_ANGLE_L2R_VIEW_THRESHOLD})")
                final_l2r_results = [best_l2r_current]
                l2r_done = True
            else:
                logger.warning(f"L2R Best Score {current_score} < {settings.MULTI_ANGLE_L2R_VIEW_THRESHOLD}.")
                # Update prompt for next time if retries left
                feedback = best_l2r_current.get('feedback') or ""
                if not feedback:
                    feedback = "No feedback provided."
                current_l2r_prompt = (
                    current_l2r_prompt.rstrip()
                    + "\n\n"
                    + "REGENERATION FEEDBACK (FROM CRITIC -- MUST FIX)\n"
                    + str(feedback)
                )
                logger.info("Updated L2R Prompt with feedback.")
                # Keep track of best failure in case we run out of retries
                if not final_l2r_results or current_score > get_score(final_l2r_results[0]):
                    final_l2r_results = [best_l2r_current]

        # Log & Process Straight View
        if not straight_done and straight_results:
            logger.info("=== Straight View Results (Current Iteration) ===")
            for res in straight_results:
                logger.info(f"Score: {res.get('score', 0)} | Path: {res.get('output_path', '')} | Feedback: {res.get('feedback', '')}")
            
            def get_score(item):
                val = item.get('score', 0)
                try: 
                    return float(val) if val is not None else 0
                except: return 0
                
            best_straight_current = sorted(straight_results, key=get_score, reverse=True)[0]
            current_score = get_score(best_straight_current)
            
            # Check threshold
            if current_score >= settings.MULTI_ANGLE_STRAIGHT_VIEW_THRESHOLD:
                logger.info(f"Straight View Passed Threshold ({current_score} >= {settings.MULTI_ANGLE_STRAIGHT_VIEW_THRESHOLD})")
                final_straight_results = [best_straight_current]
                straight_done = True
            else:
                logger.warning(f"Straight View Best Score {current_score} < {settings.MULTI_ANGLE_STRAIGHT_VIEW_THRESHOLD}.")
                # Update prompt for next time
                feedback = best_straight_current.get('feedback') or ""
                if not feedback:
                    feedback = "No feedback provided."
                current_straight_prompt = (
                    current_straight_prompt.rstrip()
                    + "\n\n"
                    + "REGENERATION FEEDBACK (FROM CRITIC -- MUST FIX)\n"
                    + str(feedback)
                )
                logger.info("Updated Straight View Prompt with feedback.")
                if not final_straight_results or current_score > get_score(final_straight_results[0]):
                    final_straight_results = [best_straight_current]

        attempt += 1
        
    best_l2r = final_l2r_results
    best_straight = final_straight_results
    pipeline_end = time.perf_counter()
    duration = pipeline_end - pipeline_start   
    logger.info(f"Multi-angle view completed in " f"{format_duration(duration)}")
    
    combined_results = []

    # L2R result
    for r in final_l2r_results[:1]:
        combined_results.append({
            "url": r.get("output_path"),
            "score": r.get("score"),
            "feedback": r.get("feedback"),
            "view_type": "l2r"
        })

    # Straight view result
    for r in final_straight_results[:1]:
        combined_results.append({
            "url": r.get("output_path"),
            "score": r.get("score"),
            "feedback": r.get("feedback"),
            "view_type": "straight"
        })

    return combined_results
