
import sys
import os
import asyncio
from pprint import pprint

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from pipelines import run_multi_angle_pipeline
from logger import set_log_context

async def main():
    # Set logging context
    set_log_context(
        project_id="Product_Placement_Dev",
        account="Standard",
        structure="FSDU",
        sub_brand="Color_Wonder",
        season="Spring",
        campaign_name="L2R_MultiAngle_Migration"
    )
    
    #Add the input image(selected from product step)
    input_image_path = "<>"
    
    #Add json from UI here
    json_data = "<>"
    print("Running Multi-Angle Pipeline...")
    results = await run_multi_angle_pipeline(json_data, input_image_path)
    
    print("\n=== Final Results ===")
    pprint(results)

if __name__ == "__main__":
    asyncio.run(main())