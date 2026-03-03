from app.services.ai_integration_service import record_user_feedback, graphics_background_job, colour_theme_background_job, colour_theme_refinement_background_job, graphics_refinement_background_job, fetch_status, product_background_job, product_refinement_background_job, multi_angle_background_job
from app.schemas.ai_integration_schema import RegenerationRequest, FeedbackRequest, ChoosenRequest, GraphicsRefinementRequest
from fastapi import APIRouter, status, Depends, BackgroundTasks
from app.schemas.project_stage_schema import StageForJobStatus
from app.schemas.response_schema import SuccessResponse
from app.utils.http_error_response import HTTP_ERRORS
from app.core.security import get_current_user
from app.utils.jobs import create_job_status
from uuid import uuid4

router = APIRouter(prefix="/ai", tags=["AI Integration"])

# -------------------------------------------------------------------
# AI Integration - Colour Theme
# -------------------------------------------------------------------
@router.get("/colour_theme/{project_id}", response_model=SuccessResponse, status_code=status.HTTP_200_OK,
responses={401: HTTP_ERRORS[401], 500: HTTP_ERRORS[500]})
async def ai_colour_theme(
    project_id: str,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_user)
):
    job_id = str(uuid4())
    stage = StageForJobStatus.Theme
    created_by = current_user["id"]
    create_job_status(job_id, project_id, stage, created_by)
    background_tasks.add_task(
        colour_theme_background_job,
        project_id,
        job_id,
    )
    return SuccessResponse(
        message="Colour theme generation started",
        data={"job_id": job_id, "status": "IN_PROGRESS"}
    )


# -------------------------------------------------------------------
# AI Integration - Colour Theme Refinement
# -------------------------------------------------------------------
@router.post("/colour_theme_refinement/{project_id}", response_model=SuccessResponse, status_code=status.HTTP_200_OK,
responses={401: HTTP_ERRORS[401], 500: HTTP_ERRORS[500]})
async def ai_colour_theme_refinement(
    project_id: str,
    body: RegenerationRequest,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_user)
):
    job_id = str(uuid4())
    stage = StageForJobStatus.Theme_Refinement
    created_by = current_user["id"]
    create_job_status(job_id, project_id, stage, created_by)
    background_tasks.add_task(
        colour_theme_refinement_background_job,
        project_id,
        body,
        job_id,
    )
    return SuccessResponse(
        message="Colour Theme Refinement started",
        data={"job_id": job_id, "status": "IN_PROGRESS"}
    )

# -------------------------------------------------------------------
# AI Integration - Graphics
# -------------------------------------------------------------------
@router.post("/graphics/{project_id}", response_model=SuccessResponse, status_code=status.HTTP_200_OK,
responses={401: HTTP_ERRORS[401], 500: HTTP_ERRORS[500]})
async def ai_graphics(
    project_id: str,
    body: ChoosenRequest,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_user)
): 
    job_id = str(uuid4())
    stage = StageForJobStatus.Graphics
    created_by = current_user["id"]
    create_job_status(job_id, project_id, stage, created_by)
    background_tasks.add_task(
        graphics_background_job,
        project_id,
        body,
        job_id,
    )
    return SuccessResponse(
        message="Graphics generation started",
        data={"job_id": job_id, "status": "IN_PROGRESS"}
    )


# -------------------------------------------------------------------
# AI Integration - Graphics Refinement
# -------------------------------------------------------------------
@router.post("/graphics_refinement/{project_id}", response_model=SuccessResponse, status_code=status.HTTP_200_OK,
responses={401: HTTP_ERRORS[401], 500: HTTP_ERRORS[500]})
async def ai_graphics_refinement(
    project_id: str,
    body: GraphicsRefinementRequest,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_user)
):
    job_id = str(uuid4())
    stage = StageForJobStatus.Graphics_Refinement
    created_by = current_user["id"]
    create_job_status(job_id, project_id, stage, created_by)
    background_tasks.add_task(
        graphics_refinement_background_job,
        project_id,
        body,
        job_id,
    )
    return SuccessResponse(
        message="Graphics Refinement started",
        data={"job_id": job_id, "status": "IN_PROGRESS"}
    )


# -------------------------------------------------------------------
# Get Job Status
# -------------------------------------------------------------------
@router.get("/status/{job_id}", response_model=SuccessResponse, status_code=status.HTTP_200_OK,
responses={401: HTTP_ERRORS[401], 500: HTTP_ERRORS[500]})
async def job_status(job_id: str,  current_user=Depends(get_current_user)):
    status = await fetch_status(job_id)
    return SuccessResponse(
        message="Job status fetched successfully",
        data=status
    )


# -------------------------------------------------------------------
# AI Integration - Product Placement
# -------------------------------------------------------------------
@router.post("/product_placement/{project_id}", response_model=SuccessResponse, status_code=status.HTTP_200_OK,
responses={401: HTTP_ERRORS[401], 500: HTTP_ERRORS[500]})
def ai_product_placement(
    project_id: str,
    body: ChoosenRequest,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_user)
):
    job_id = str(uuid4())
    stage = StageForJobStatus.Product
    created_by = current_user["id"]
    create_job_status(job_id, project_id, stage, created_by)
    background_tasks.add_task(
        product_background_job,
        project_id,
        body,
        job_id,
    )
    return SuccessResponse(
        message="Product Placement started",
        data={"job_id": job_id, "status": "IN_PROGRESS"}
    )


# -------------------------------------------------------------------
# AI Integration - Product Placement Refinement
# -------------------------------------------------------------------
@router.post("/product_placement_refinement/{project_id}", response_model=SuccessResponse, status_code=status.HTTP_200_OK,
responses={401: HTTP_ERRORS[401], 500: HTTP_ERRORS[500]})
async def ai_product_placement_refinement(
    project_id: str,
    body: RegenerationRequest,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_user)
):
    job_id = str(uuid4())
    stage = StageForJobStatus.Product_Refinement
    created_by = current_user["id"]
    create_job_status(job_id, project_id, stage, created_by)
    background_tasks.add_task(
        product_refinement_background_job,
        project_id,
        body,
        job_id,
    )
    return SuccessResponse(
        message="Product Placement Refinement started",
        data={"job_id": job_id, "status": "IN_PROGRESS"}
    )


# -------------------------------------------------------------------
# AI Integration - Feedback
# -------------------------------------------------------------------
@router.post("/feedback/{project_id}", response_model=SuccessResponse, status_code=status.HTTP_200_OK,
responses={401: HTTP_ERRORS[401], 500: HTTP_ERRORS[500]})
def ai_feedback(
    project_id: str,
    body: FeedbackRequest,
    current_user=Depends(get_current_user)
):
    results = record_user_feedback(project_id, body, current_user)
    return SuccessResponse(message="User Feedback recorded ", data=results)


# -------------------------------------------------------------------
# AI Integration - Multi Angle View
# -------------------------------------------------------------------
@router.post("/multi_angle_view/{project_id}", response_model=SuccessResponse, status_code=status.HTTP_200_OK,
responses={401: HTTP_ERRORS[401], 500: HTTP_ERRORS[500]})
async def ai_multi_angle_view(
    project_id: str,
    body: ChoosenRequest,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_user)
):
    job_id = str(uuid4())
    stage = StageForJobStatus.Multi_Angle_View
    created_by = current_user["id"]
    create_job_status(job_id, project_id, stage, created_by)
    background_tasks.add_task(
        multi_angle_background_job,
        project_id,
        body,
        job_id,
    )
    return SuccessResponse(
        message="Multi Angle View job started",
        data={"job_id": job_id, "status": "IN_PROGRESS"}
    )