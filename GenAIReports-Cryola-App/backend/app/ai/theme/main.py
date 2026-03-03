import os
import sys
import asyncio
import logging
import argparse
from openai import AzureOpenAI

# ==========================================
# 1. ROBUST PATH SETUP
# ==========================================

current_file = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file)
# Go up 3 levels: theme ->  - > AI - > app -> backend -> [ROOT]
project_root = os.path.abspath(os.path.join(current_dir, "../../../../"))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

# ==========================================
# 2. IMPORTS (FULL PACKAGE PATH)
# ==========================================


from backend.app.ai.theme.config import Config
from backend.app.ai.theme.logger import set_log_context, get_logger, get_current_log_filepath
from backend.app.ai.theme.storage import BlobManager
from backend.app.ai.theme.pipelines import run_theme_initial, run_theme_refinement

# ==========================================
# 3. SETUP & EXECUTION
# ==========================================

# (Environment variables setup )
"""
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "") 
AZURE_STORAGE_ACCOUNT_NAME = os.getenv("AZURE_STORAGE_ACCOUNT_NAME", "")
AZURE_STORAGE_ACCOUNT_KEY = os.getenv("AZURE_STORAGE_ACCOUNT_KEY", "")
AZURE_BLOB_CONTAINER = os.getenv("AZURE_BLOB_CONTAINER", "")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
"""


async def test_initial():
    print("\n>>> STARTING: INITIAL THEME GENERATION")
    
    set_log_context(
        project_id = "P_123",
        account="Walmart", 
        structure="CW_Mini_Box_Floor_Stand",
        sub_brand="CokeZero",
        season="Summer2025",
        campaign_name="Refresh"
    )

    logging.getLogger("ThemeEngine").handlers.clear()
    logger = get_logger("ThemeEngine")
    logger.info("----- LOGGING STARTED (INITIAL) -----")
    
    client = AzureOpenAI(
        api_key=AZURE_OPENAI_API_KEY,
        api_version=Config.IMAGE_API_VERSION,
        azure_endpoint=AZURE_OPENAI_ENDPOINT
    )

    #Add blob url of the input image here
    input_url = ""
    hex_code = "#B79611"

    print(f"Processing: {input_url}")
    results = await run_theme_initial(client, input_blob_url=input_url, hex_code=hex_code)
    
    print(f"\nGenerated {len(results)} images:")
    for r in results:
        print(f" Score: {r['score']} | URL: {r['url']}")

    BlobManager().upload_and_cleanup_log()

async def test_refinement():
    print("\n>>> STARTING: THEME REFINEMENT")

    set_log_context(
        project_id = "P_123",
        account="Walmart", 
        structure="CW_Mini_Box_Floor_Stand",
        sub_brand="CokeZero",
        season="Summer2025",
        campaign_name="Refresh"
    )

    logging.getLogger("ThemeEngine").handlers.clear()
    logger = get_logger("ThemeEngine")
    logger.info("----- LOGGING STARTED (REFINEMENT) -----")

    client = AzureOpenAI(
        api_key=AZURE_OPENAI_API_KEY,
        api_version=Config.IMAGE_API_VERSION,
        azure_endpoint=AZURE_OPENAI_ENDPOINT
    )

    #Add blob url of the input image here which the user selected on UI
    chosen_url = ""
    #Add User feedback here
    feedback = " "

    print(f"Refining Image: {chosen_url}")
    final_res = await run_theme_refinement(client, chosen_url, feedback)

    if final_res:
        print("\n=== FINAL RESULT ===")
        print(f"URL: {final_res['url']}")
        print(f"SCORE: {final_res['score']}")
   
    BlobManager().upload_and_cleanup_log()



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test AI Theme Pipelines")
    parser.add_argument('mode', choices=['initial', 'refinement'], help="Which pipeline to run")
    
    args = parser.parse_args()
    
    """if os.environ["AZURE_OPENAI_API_KEY"] == "<your-key>":
        print("!! ERROR: Please update AZURE_OPENAI_API_KEY in main.py !!")
        sys.exit(1)"""

    if args.mode == 'initial':
        asyncio.run(test_initial())
    elif args.mode == 'refinement':
        asyncio.run(test_refinement())