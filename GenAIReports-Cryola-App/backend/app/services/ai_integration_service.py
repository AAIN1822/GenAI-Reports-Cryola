from app.schemas.ai_integration_schema import FeedbackRequest, ChoosenRequest, GraphicsRefinementRequest, RegenerationRequest
from app.ai.product.pipelines import run_product_placement_initial_pipeline, run_product_refinement_pipeline
from app.ai.graphics.pipelines import run_graphics_initial_pipeline, run_graphics_refinement_pipeline
from app.db.db_config import PROJECTS_CONTAINER, FEEDBACK_CONTAINER, JOBS_CONTAINER
from app.ai.theme.pipelines import run_theme_initial, run_theme_refinement
from app.utils.jobs import update_job_status, extract_error_message
from app.ai.multi_angle.pipelines import run_multi_angle_pipeline
from azure.cosmos.exceptions import CosmosResourceNotFoundError
from app.schemas.project_stage_schema import ProjectStage
from app.utils.regex_blob_name import sanitize_blob_name
from app.utils.datetime_helper import utc_unix
from app.ai.theme.storage import BlobManager
from app.ai.theme.logger import  get_logger
from fastapi import HTTPException, status
from app.ai.theme.config import Config
from app.core.config import settings
from app.db.session import get_db
from openai import AzureOpenAI
from io import StringIO
from uuid import uuid4
import logging

client = AzureOpenAI(
    api_key=settings.AZURE_OPENAI_API_KEY,
    api_version=Config.IMAGE_API_VERSION,
    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT
)

def build_folder_name(project):
    def clean(x):
        return str(x).replace(" ", "_").replace("/", "_").replace("\\", "_")

    folder = (
        f"{clean(project.get('account', 'NA'))}/"
        f"{clean(project.get('structure', 'NA'))}/"
        f"{clean(project.get('sub_brand', 'NA'))}/"
        f"{clean(project.get('season', 'NA'))}/"
        f"{clean(project.get('region', 'NA'))}/"
        f"{clean(project.get('project_description', 'NA'))}_"
        f"{clean(project.get('id', 'NA'))}"
    )
    folder_name = sanitize_blob_name(folder)
    return folder_name

# Generate colour theme based on FSDU image and color code
async def colour_theme(project_id: str):
    db = get_db()
    project_container = db[PROJECTS_CONTAINER]
    try:
        query = "SELECT * FROM c WHERE c.id = @project_id"
        params = [{"name": "@project_id", "value": project_id}]
        results = list(project_container.query_items(
            query=query, 
            parameters=params, 
            enable_cross_partition_query=True
            ))

        if not results:
            raise HTTPException(status_code=404, detail="Project not found")

        project = results[0]
        fsdu_image = project.get("details", {}).get("fsdu", {}).get("image")
        color_code = project.get("details", {}).get("color")
        folder_name = build_folder_name(project)

        log_buffer = StringIO()
        handler = logging.StreamHandler(log_buffer)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
        handler.setFormatter(formatter)
        logger = get_logger("ThemeEngine_Pipelines")
        logger = get_logger("ThemeEngine_Services")
        logger = get_logger("ThemeEngine_Storage")
        # Attach handler to ALL loggers starting with 'ThemeEngine'
        for name, logger_obj in logging.Logger.manager.loggerDict.items():
            if isinstance(logger_obj, logging.Logger) and name.startswith("ThemeEngine"):
                logger_obj.handlers.clear()
                logger_obj.addHandler(handler)

        logger.info("==== API CALL: Colour Theme Generation Started ====")
        logger.info(f"Project ID: {project_id}")
        logger.info(f"Input Image: {fsdu_image}")
        logger.info(f"HEX Color: {color_code}")

        theme_results = await run_theme_initial(client, fsdu_image, color_code, folder_name)
        logger.info("=== Theme Generation Completed Successfully ===")
        project["stage"] = ProjectStage.STAGE_3
        project["ai_colour_theme_results"] = theme_results
        project_container.replace_item(
            item=project["id"],
            body=project
        )
        logger.info("Uploading logs to Blob Storage...")
        log_text = log_buffer.getvalue()
        BlobManager().append_project_log(folder_name, log_text)
        return theme_results

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# Refine theme based on user feedback
async def colour_theme_refinement(project_id: str, choosen_url: str, feedback_prompt: str):
    db = get_db()
    project_container = db[PROJECTS_CONTAINER]
    try:
        query = "SELECT * FROM c WHERE c.id = @project_id"
        params = [{"name": "@project_id", "value": project_id}]
        results = list(project_container.query_items(
            query=query,
            parameters=params,
            enable_cross_partition_query=True
        ))
        if not results:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project = results[0]
        folder_name = build_folder_name(project)
        log_buffer = StringIO()
        handler = logging.StreamHandler(log_buffer)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
        handler.setFormatter(formatter)
        logger = get_logger("ThemeEngine_Pipelines")
        logger = get_logger("ThemeEngine_Services")
        logger = get_logger("ThemeEngine_Storage")
        for name, logger_obj in logging.Logger.manager.loggerDict.items():
            if isinstance(logger_obj, logging.Logger) and name.startswith("ThemeEngine"):
                logger_obj.handlers.clear()
                logger_obj.addHandler(handler)

        logger.info("==== API CALL: Colour_Theme Refinement Started ====")
        logger.info(f"Project ID: {project_id}")
        logger.info(f"Chosen URL: {choosen_url}")
        logger.info(f"Feedback Prompt: {feedback_prompt}")

        refinement_result = await run_theme_refinement(client, choosen_url, feedback_prompt, folder_name)
        
        refinement_entry = {
            **refinement_result,
            "feedback_prompt": feedback_prompt
        }
        existing_list = project.get("ai_colour_theme_refinement", [])

        if not isinstance(existing_list, list):
            existing_list = []
        
        existing_list.append(refinement_entry)
        project["ai_colour_theme_refinement"] = existing_list
        project["stage"] = ProjectStage.STAGE_4
        project_container.replace_item(
            item=project["id"],
            body=project
        )
        log_text = log_buffer.getvalue()
        BlobManager().append_project_log(folder_name, log_text)
        return refinement_entry
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

# Generate graphics based on chosen design
async def graphics(project_id: str, body: ChoosenRequest):
    db = get_db()
    project_container = db[PROJECTS_CONTAINER]
    try:
        query = "SELECT * FROM c WHERE c.id = @project_id"
        params = [{"name": "@project_id", "value": project_id}]
        results = list(project_container.query_items(
            query=query, 
            parameters=params, 
            enable_cross_partition_query=True
            ))

        if not results:
            raise HTTPException(status_code=404, detail="Project not found")

        project = results[0]
        header_image = project.get("details", {}).get("header", {}).get("image") or None
        footer_image = project.get("details", {}).get("footer", {}).get("image") or None
        sidepanel_image = project.get("details", {}).get("sidepanel", {}).get("image") or None
        shelf_image = project.get("details", {}).get("shelf", {}).get("image") or None

        folder_name = build_folder_name(project)

        log_buffer = StringIO()
        handler = logging.StreamHandler(log_buffer)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
        handler.setFormatter(formatter)
        logger = get_logger("Graphics_Pipeline")
        logger = get_logger("Graphics_Services")
        logger = get_logger("Graphics_Storage")
        # Attach handler to ALL loggers starting with 'Graphics'
        for name, logger_obj in logging.Logger.manager.loggerDict.items():
            if isinstance(logger_obj, logging.Logger) and name.startswith("Graphics"):
                logger_obj.handlers.clear()
                logger_obj.addHandler(handler)

        logger.info("==== API CALL: Graphics Generation Started ====")
        logger.info(f"Project ID: {project_id}")
        logger.info(f"Header Image: {header_image}")
        logger.info(f"Footer Image: {footer_image}")
        logger.info(f"Sidepanel Image: {sidepanel_image}")
        logger.info(f"Shelf Image: {shelf_image}")
        logger.info(f"Choosen URL: {body.choosen_url}")
        logger.info(f"Score: {body.score}")

        graphics_results = await run_graphics_initial_pipeline(folder_name, body.choosen_url, header_image, sidepanel_image, shelf_image, footer_image)
        logger.info("=== Theme Generation Completed Successfully ===")
        project["stage"] = ProjectStage.STAGE_5
        project["ai_graphics_input"] = body.choosen_url
        project["ai_graphics_results"] = graphics_results
        project_container.replace_item(
            item=project["id"],
            body=project
        )
        logger.info("Uploading logs to Blob Storage...")
        log_text = log_buffer.getvalue()
        BlobManager().append_project_log(folder_name, log_text)
        return graphics_results

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Refine graphics based on user feedback
async def graphics_refinement(project_id: str, body: GraphicsRefinementRequest):
    db = get_db()
    project_container = db[PROJECTS_CONTAINER]
    try:
        query = "SELECT * FROM c WHERE c.id = @project_id"
        params = [{"name": "@project_id", "value": project_id}]
        results = list(project_container.query_items(
            query=query,
            parameters=params,
            enable_cross_partition_query=True
        ))
        if not results:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project = results[0]
        base_image_url = project.get("ai_graphics_input")
        header_image = project.get("details", {}).get("header", {}).get("image") or None
        footer_image = project.get("details", {}).get("footer", {}).get("image") or None
        sidepanel_image = project.get("details", {}).get("sidepanel", {}).get("image") or None
        shelf_image = project.get("details", {}).get("shelf", {}).get("image") or None
                
        folder_name = build_folder_name(project)

        log_buffer = StringIO()
        handler = logging.StreamHandler(log_buffer)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
        handler.setFormatter(formatter)
        logger = get_logger("Graphics_Pipeline")
        logger = get_logger("Graphics_Services")
        logger = get_logger("Graphics_Storage")
        # Attach handler to ALL loggers starting with 'Graphics'
        for name, logger_obj in logging.Logger.manager.loggerDict.items():
            if isinstance(logger_obj, logging.Logger) and name.startswith("Graphics"):
                logger_obj.handlers.clear()
                logger_obj.addHandler(handler)

        logger.info("==== API CALL: Graphics Refinement Started ====")
        logger.info(f"Project ID: {project_id}")
        logger.info(f"Header Image: {header_image}")
        logger.info(f"Footer Image: {footer_image}")
        logger.info(f"Sidepanel Image: {sidepanel_image}")
        logger.info(f"Shelf Image: {shelf_image}")
        logger.info(f"Selected Graphics URL: {body.selected_graphics_url}")
        logger.info(f"Selected Colour Theme URL: {base_image_url}")
        logger.info(f"Feedback Prompt: {body.feedback_prompt}")

        refinement_result = await run_graphics_refinement_pipeline(folder_name, body.feedback_prompt, body.selected_graphics_url, base_image_url, header_image, sidepanel_image, shelf_image, footer_image)
        
        refinement_entry = {
            **refinement_result,
            "feedback_prompt": body.feedback_prompt
        }
        existing_list = project.get("ai_graphics_refinement", [])

        if not isinstance(existing_list, list):
            existing_list = []
        
        existing_list.append(refinement_entry)
        project["ai_graphics_refinement_input"] = body.selected_graphics_url
        project["ai_graphics_refinement"] = existing_list
        project["stage"] = ProjectStage.STAGE_6
        project_container.replace_item(
            item=project["id"],
            body=project
        )
        log_text = log_buffer.getvalue()
        BlobManager().append_project_log(folder_name, log_text)
        return refinement_entry
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

# Record user feedback
def record_user_feedback(project_id: str, body: FeedbackRequest, current_user):
    db = get_db()
    feedback_container = db[FEEDBACK_CONTAINER]
    try:
        user_id = current_user["id"]
        query = """
        SELECT * FROM c 
        WHERE c.project_id = @project_id 
        AND c.image_url = @image_url
        """
        params = [
            {"name": "@project_id", "value": project_id},
            {"name": "@image_url", "value": body.image_url}
        ]
        items = list(feedback_container.query_items(
            query=query,
            parameters=params,
            enable_cross_partition_query=True
        ))
        if items:
            existing = items[0]
            existing["like"] = body.like
            existing["stage"] = body.stage
            existing["created_at"] = utc_unix()
            existing["user_id"] = user_id

            feedback_container.replace_item(
                item=existing["id"],
                body=existing
            )
        else:
            new_doc = {
                "id": str(uuid4()),
                "user_id": user_id,
                "project_id": project_id,
                "image_url": body.image_url,
                "like": body.like,
                "stage": body.stage,
                "created_at": utc_unix()
            }
            feedback_container.create_item(new_doc)
        return {
            "url": body.image_url,
            "like": body.like,
            "stage": body.stage
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

# Product Placement generation
async def product_placement(project_id: str, body: ChoosenRequest):
    db = get_db()
    project_container = db[PROJECTS_CONTAINER]
    try:
        query = "SELECT * FROM c WHERE c.id = @project_id"
        params = [{"name": "@project_id", "value": project_id}]
        results = list(project_container.query_items(
            query=query,
            parameters=params,
            enable_cross_partition_query=True
        ))
        if not results:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project = results[0]
        #products = project.get("details", {}).get("products", {}) or None
                
        folder_name = build_folder_name(project)

        log_buffer = StringIO()
        handler = logging.StreamHandler(log_buffer)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
        handler.setFormatter(formatter)
        logger = get_logger("Product_Placement_Pipeline")
        logger = get_logger("Product_Placement_Services")
        logger = get_logger("Product_Placement_Storage")
        # Attach handler to ALL loggers starting with 'Product'
        for name, logger_obj in logging.Logger.manager.loggerDict.items():
            if isinstance(logger_obj, logging.Logger) and name.startswith("Product"):
                logger_obj.handlers.clear()
                logger_obj.addHandler(handler)

        logger.info("==== API CALL: Product Placement Started ====")
        logger.info(f"Project ID: {project_id}")
        logger.info(f"Selected Graphics Image URL: {body.choosen_url}")

        product_result = await run_product_placement_initial_pipeline(project, body.choosen_url, folder_name)

        project["stage"] = ProjectStage.STAGE_7
        project["ai_product_placement_input"] = body.choosen_url
        project["ai_product_placement_results"] = product_result
        project_container.replace_item(
            item=project["id"],
            body=project
        )
        logger.info("Uploading logs to Blob Storage...")
        log_text = log_buffer.getvalue()
        BlobManager().append_project_log(folder_name, log_text)
        return product_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

# Refine product placement based on user feedback
async def product_placement_refinement(project_id: str, body: RegenerationRequest):
    db = get_db()
    project_container = db[PROJECTS_CONTAINER]
    try:
        query = "SELECT * FROM c WHERE c.id = @project_id"
        params = [{"name": "@project_id", "value": project_id}]
        results = list(project_container.query_items(
            query=query,
            parameters=params,
            enable_cross_partition_query=True
        ))
        if not results:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project = results[0]
        #products = project.get("details", {}).get("products", {}) or None
        graphics_output = project.get("ai_product_placement_input")   
        folder_name = build_folder_name(project)

        log_buffer = StringIO()
        handler = logging.StreamHandler(log_buffer)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
        handler.setFormatter(formatter)
        logger = get_logger("Product_Placement_Pipeline")
        logger = get_logger("Product_Placement_Services")
        logger = get_logger("Product_Placement_Storage")
        # Attach handler to ALL loggers starting with 'Product'
        for name, logger_obj in logging.Logger.manager.loggerDict.items():
            if isinstance(logger_obj, logging.Logger) and name.startswith("Product"):
                logger_obj.handlers.clear()
                logger_obj.addHandler(handler)

        logger.info("==== API CALL: Product Placement Refinement Started ====")
        logger.info(f"Project ID: {project_id}")
        logger.info(f"Selected Product URL: {body.choosen_url}")
        logger.info(f"Feedback Prompt: {body.feedback_prompt}")
        logger.info(f"Graphics Output URL: {graphics_output}")

        refinement_result = await run_product_refinement_pipeline(body.feedback_prompt, body.choosen_url, graphics_output, project, folder_name)
        
        refinement_entry = {
            **refinement_result,
            "feedback_prompt": body.feedback_prompt
        }
        existing_list = project.get("ai_product_placement_refinement", [])

        if not isinstance(existing_list, list):
            existing_list = []
        
        existing_list.append(refinement_entry)
        project["ai_product_placement_refinement_input"] = body.choosen_url
        project["ai_product_placement_refinement"] = existing_list
        project["stage"] = ProjectStage.STAGE_8
        project_container.replace_item(
            item=project["id"],
            body=project
        )
        log_text = log_buffer.getvalue()
        BlobManager().append_project_log(folder_name, log_text)
        return refinement_entry
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

# Multi Angle View generation
async def multi_angle_view(project_id: str, body: ChoosenRequest):
    input_url = body.choosen_url
    score = body.score
    db = get_db()
    project_container = db[PROJECTS_CONTAINER]
    try:
        query = "SELECT * FROM c WHERE c.id = @project_id"
        params = [{"name": "@project_id", "value": project_id}]
        results = list(project_container.query_items(
            query=query,
            parameters=params,
            enable_cross_partition_query=True
        ))
        if not results:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project = results[0] 
        folder_name = build_folder_name(project)

        log_buffer = StringIO()
        handler = logging.StreamHandler(log_buffer)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
        handler.setFormatter(formatter)
        logger = get_logger("MultiAngle_Pipeline")
        logger = get_logger("MultiAngle_Services")
        logger = get_logger("MultiAngle_Storage")
        # Attach handler to ALL loggers starting with 'MultiAngle'
        for name, logger_obj in logging.Logger.manager.loggerDict.items():
            if isinstance(logger_obj, logging.Logger) and name.startswith("MultiAngle"):
                logger_obj.handlers.clear()
                logger_obj.addHandler(handler)

        logger.info("==== API CALL: Multi Angle View Generation Started ====")
        logger.info(f"Project ID: {project_id}")
        logger.info(f"Selected Product URL for Multi Angle View: {input_url}")

        multi_angle_result = await run_multi_angle_pipeline(project, input_url, folder_name)
        multi_angle_result.append({
            "url": input_url,
            "score": score,
            "feedback": "Original image provided by user for multi-angle view generation",
            "view_type": "r2l"
        })
        project["stage"] = ProjectStage.STAGE_9
        project["ai_multi_angle_view_input"] = input_url
        project["ai_multi_angle_view_results"] = multi_angle_result
        project_container.replace_item(
            item=project["id"],
            body=project
        )
        logger.info("Uploading logs to Blob Storage...")
        log_text = log_buffer.getvalue()
        BlobManager().append_project_log(folder_name, log_text)
        return multi_angle_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

# Background job for Graphics generation
async def graphics_background_job(project_id, body, job_id):
    try:
        await graphics(project_id, body)
        update_job_status(job_id, status="COMPLETED", message="Graphics generation completed successfully")
    except Exception as e:
        user_message = extract_error_message(e)
        update_job_status(job_id, status="FAILED", error=str(e), message=user_message)


# Background job for Colour_Theme generation
async def colour_theme_background_job(project_id, job_id):
    try:
        await colour_theme(project_id)
        update_job_status(job_id, status="COMPLETED", message="Colour Theme generation completed successfully")
    except Exception as e:
        user_message = extract_error_message(e)
        update_job_status(job_id, status="FAILED", error=str(e), message=user_message)


# Background job for Colour_Theme Refinement
async def colour_theme_refinement_background_job(project_id, body, job_id):
    try:
        await colour_theme_refinement(project_id, body.choosen_url, body.feedback_prompt)
        update_job_status(job_id, status="COMPLETED", message="Colour Theme Refinement completed successfully")
    except Exception as e:
        user_message = extract_error_message(e)
        update_job_status(job_id, status="FAILED", error=str(e), message=user_message)

    
# Background job for Graphics Refinement
async def graphics_refinement_background_job(project_id, body, job_id):
    try:
        await graphics_refinement(project_id, body)
        update_job_status(job_id, status="COMPLETED", message="Graphics Refinement completed successfully")
    except Exception as e:
        user_message = extract_error_message(e)
        update_job_status(job_id, status="FAILED", error=str(e), message=user_message)


# Background job for Product Placement
async def product_background_job(project_id, body, job_id):
    try:
        await product_placement(project_id, body)
        update_job_status(job_id, status="COMPLETED", message="Product Placement completed successfully")
    except Exception as e:
        user_message = extract_error_message(e)
        update_job_status(job_id, status="FAILED", error=str(e), message=user_message)


# Background job for Product Placement Refinement
async def product_refinement_background_job(project_id, body, job_id):
    try:
        await product_placement_refinement(project_id, body)
        update_job_status(job_id, status="COMPLETED", message="Product Placement Refinement completed successfully")
    except Exception as e:
        user_message = extract_error_message(e)
        update_job_status(job_id, status="FAILED", error=str(e), message=user_message)


# Background job for Multi Angle View
async def multi_angle_background_job(project_id, body, job_id):
    try:
        await multi_angle_view(project_id, body)
        update_job_status(job_id, status="COMPLETED", message="Multi Angle View generation completed successfully")
    except Exception as e:
        user_message = extract_error_message(e)
        update_job_status(job_id, status="FAILED", error=str(e), message=user_message)


# Fetch job status
async def fetch_status(job_id: str):
    db = get_db()
    jobs_container = db[JOBS_CONTAINER]
    id = job_id
    try:
        return jobs_container.read_item(
            item=job_id,
            partition_key=id
        )
    except CosmosResourceNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with id '{job_id}' not found"
        )