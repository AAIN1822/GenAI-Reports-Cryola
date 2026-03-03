from app.services.project_service import create_project, update_project_details, fetch_project_by_id, save_as, download_project, v1_fetch_all_projects
from app.schemas.project_update_schema import ProjectUpdate
from app.schemas.response_schema import SuccessResponse
from app.utils.http_error_response import HTTP_ERRORS
from fastapi import APIRouter, Query, status, Depends
from app.schemas.project_schema import ProjectCreate
from starlette.responses import StreamingResponse
from app.core.security import get_current_user

router = APIRouter(prefix="/projects", tags=["Projects"], dependencies=[Depends(get_current_user)])

# -------------------------------------------------------------------
# Create New Project
# -------------------------------------------------------------------
@router.post("/new-project", response_model=SuccessResponse, status_code=status.HTTP_200_OK,
responses={401: HTTP_ERRORS[401], 500: HTTP_ERRORS[500]})
def create_new_project(payload: ProjectCreate, current_user=Depends(get_current_user)):
    project = create_project(payload, current_user)
    return SuccessResponse(message="Project created successfully", data=project)


# -------------------------------------------------------------------
# Get Project History with pagination
# -------------------------------------------------------------------
@router.get("/history", response_model=SuccessResponse, status_code=status.HTTP_200_OK,
responses={401: HTTP_ERRORS[401], 500: HTTP_ERRORS[500]})
def v1_get_project_history(
    search: str | None = Query(None, description="Search projects"),
    account: str | None = Query(None),
    structure: str | None = Query(None),
    sub_brand: str | None = Query(None),
    season: str | None = Query(None),
    region: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = Query(
        "created_at",
        description="account|structure|sub_brand|season|region|project_description|created_at",
    ),
    sort_order: str = Query("desc", description="asc|desc"),
    current_user=Depends(get_current_user),
):
    projects = v1_fetch_all_projects(
        search=search,
        filters={
            "account": account,
            "structure": structure,
            "sub_brand": sub_brand,
            "season": season,
            "region": region,
        },
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
        current_user=current_user,
    )
    return SuccessResponse(
        message="Project history fetched successfully", data=projects
    )


# -------------------------------------------------------------------
# Update Project Details
# -------------------------------------------------------------------
@router.put("/{project_id}/update", response_model=SuccessResponse, status_code=status.HTTP_200_OK,
responses={401: HTTP_ERRORS[401], 500: HTTP_ERRORS[500]})
def update_project(project_id: str, payload: ProjectUpdate, current_user=Depends(get_current_user)):
    data = payload.model_dump(exclude_none=True, mode="json")
    updated = update_project_details(project_id, data, current_user)
    return SuccessResponse(message="Project updated successfully", data=updated)


# -------------------------------------------------------------------
# Get Project by ID
# -------------------------------------------------------------------
@router.get("/{project_id}", response_model=SuccessResponse, status_code=status.HTTP_200_OK,
responses={401: HTTP_ERRORS[401], 404: HTTP_ERRORS[404]})
def get_project(project_id: str, current_user=Depends(get_current_user)):
    project = fetch_project_by_id(project_id, current_user)
    return SuccessResponse(
        message="Project fetched successfully",
        data=project
    )


# -------------------------------------------------------------------
# Save As project
# -------------------------------------------------------------------
@router.post("/save_as/{project_id}", response_model=SuccessResponse, status_code=status.HTTP_200_OK,
responses={401: HTTP_ERRORS[401], 500: HTTP_ERRORS[500]})
def save_as_project(
    project_id: str,
    payload: ProjectCreate,
    current_user=Depends(get_current_user)
):
    new_project = save_as(project_id, payload, current_user)
    return SuccessResponse(
        message="Project Saved as new project successfully",
        data=new_project
    )


# -------------------------------------------------------------------
# Download Project Files
# -------------------------------------------------------------------
@router.get("/download_project/{project_id}", response_class=StreamingResponse, status_code=status.HTTP_200_OK,
responses={401: HTTP_ERRORS[401], 500: HTTP_ERRORS[500]})
def download_project_files(
    project_id: str,
    current_user=Depends(get_current_user)
):
    results = download_project(project_id, current_user)
    return results
