from app.schemas.project_update_schema import ProjectUpdate
from app.services.dam_service import update_project_details
from app.schemas.response_schema import SuccessResponse
from app.utils.http_error_response import HTTP_ERRORS
from app.services.dam_service import list_images
from app.core.security import get_current_user
from fastapi import APIRouter, Depends
from fastapi import status, Query

router = APIRouter(prefix="/dam", tags=["DAM"])

# -------------------------------------------------------------------
# Get images from Acquia DAM
# -------------------------------------------------------------------
@router.get("/image-listing", response_model=SuccessResponse, status_code=status.HTTP_200_OK,
responses={401: HTTP_ERRORS[401], 500: HTTP_ERRORS[500]})
def get_gallery(
    search: str | None = Query(None, description="Search by image name"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user=Depends(get_current_user)
):
    images = list_images(search, page, page_size)
    return SuccessResponse(message="DAM images fetched successfully", data=images)


# -------------------------------------------------------------------
# Update Project Details
# -------------------------------------------------------------------
@router.put("/{project_id}/update", response_model=SuccessResponse, status_code=status.HTTP_200_OK,
responses={401: HTTP_ERRORS[401], 500: HTTP_ERRORS[500]})
def update_project(project_id: str, payload: ProjectUpdate, current_user=Depends(get_current_user)):
    data = payload.model_dump(exclude_none=True, mode="json")
    updated = update_project_details(project_id, data, current_user)
    return SuccessResponse(message="Project updated successfully", data=updated)
