
import sys
import os
import asyncio
from pprint import pprint

# Ensure the backend directory is in the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from app.ai.product.pipelines import run_product_placement_initial_pipeline
from app.ai.graphics.logger import set_log_context

async def main():
    # Set logging context
    set_log_context(
        project_id="Product_Placement_Dev",
        account="Standard",
        structure="FSDU",
        sub_brand="Color_Wonder",
        season="Spring",
        campaign_name="Initial_Migration"
    )

    json_data = "<>"

    fsdu_path = "<>"

    # Call Orchestrator
    results = await run_product_placement_initial_pipeline(json_data, fsdu_path)
    
    print("\n=== Final Results ===")
    for res in results:
        print(f"Score: {res.get('score', 0):.2f} | URL: {res.get('generated_image_path', 'N/A')}")


if __name__ == "__main__":
    asyncio.run(main())
