import argparse 
import asyncio
import sys
from .pipelines import run_graphics_initial_pipeline, run_graphics_refinement_pipeline
from .logger import get_logger
import os
from pathlib import Path
import logging
from .logger import set_log_context

logger = get_logger("Graphics_Main")

async def test_graphics_initial():
    # For testing, we can use local paths (using file:// protocol is handled by storage.py fallback)
    # OR blob URLs if available.
    
    set_log_context(
        project_id = "P_123",
        account="Walmart", 
        structure="CW_Display_Stand",
        sub_brand="Color Wonder",
        season="Winter2025",
        campaign_name="Refresh"
    )

    logging.getLogger("GraphicsEngine").handlers.clear()
    logger = get_logger("GraphicsEngine")
    logger.info("----- LOGGING STARTED (INITIAL) -----")
    # IMPORTANT: Update these paths to point to actual test files
    base_shelf_path  = "<base_structure_path>"
    header_path      = "<header_path>"    #optional else None
    side_path        = "<side_path>"    #optional else None
    front_lip_path   = "<front_lip_path>"   #optional else None
    plinth_path      = "<plinth_path>"    #optional else None
    
       
    logger.info("Starting Graphics Initial Pipeline...")
    try:
        result_urls = await run_graphics_initial_pipeline(
            folder_name="test_graphics_initial",
            base_shelf_url=base_shelf_path,
            header_url=header_path,
            side_url=side_path,
            front_lip_url=front_lip_path,
            plinth_url=plinth_path,
            # Add the applicable graphics as needed, rest to be sent as None
        )
        #print("\n=== Final Results ===")
        #print("Prompt length:", len(final_prompt))
        for res in result_urls:
            print(f"Score: {res['score']:.2f} | URL: {res['url']}")
    except Exception as e:
        logger.exception("Pipeline failed")

async def test_graphics_refinement():

    set_log_context(
        project_id = "P_123",
        account="Walmart", 
        structure="CW_Power_Panel",
        sub_brand="Color Wonder",
        season="Winter2025",
        campaign_name="Refresh"
    )
    logging.getLogger("GraphicsEngine").handlers.clear()
    logger = get_logger("GraphicsEngine")
    logger.info("----- LOGGING STARTED (REFINEMENT) -----")

    # User feedback
    user_feedback = """<user_feedback"""

    # IMPORTANT: Update these paths to point to actual test files, along with user selected output path - the same inputs as initial pipeline   
    selected_output_path = "<selected_output_path>"
    base_shelf_path  = "<base_structure_path>"
    header_path      = "<header_path>"    #optional else None
    side_path        = "<side_path>"    #optional else None
    front_lip_path   = "<front_lip_path>"   #optional else None
    plinth_path      = "<plinth_path>"    #optional else None


    try:
        refined_result = await run_graphics_refinement_pipeline(
            folder_name="test_graphics_refinement",
            user_feedback = user_feedback,
            selected_output_url=selected_output_path,
            base_shelf_url= base_shelf_path,
            header_url = header_path,
            side_url= side_path,
            front_lip_url= front_lip_path,
            plinth_url=plinth_path
        )
        print(f"Score: {refined_result['score']:.2f} | URL: {refined_result['url']}")
    except Exception as e:
        logger.exception("Pipeline failed")
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test AI Graphics Pipelines")
    parser.add_argument('mode', choices=['initial', 'refinement'], help="Which pipeline to run")
    
    args = parser.parse_args()
    
    """if os.environ["AZURE_OPENAI_API_KEY"] == "<your-key>":
        print("!! ERROR: Please update AZURE_OPENAI_API_KEY in main.py !!")
        sys.exit(1)"""

    if args.mode == 'initial':
        asyncio.run(test_graphics_initial())
    elif args.mode == 'refinement':
        asyncio.run(test_graphics_refinement())


