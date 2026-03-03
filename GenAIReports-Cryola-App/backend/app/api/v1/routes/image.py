from app.services.image_service import delete_image_from_blob, refinement_image_upload, save_refinement_to_cosmos, delete_refinement, upload_image_v1, v1_image_exist_in_blob, create_thumbnail
from app.services.gallery_service import save_upload_record, delete_upload_record, v1_list_images
from fastapi import APIRouter, UploadFile, Form, Depends, File, Query
from app.schemas.response_schema import SuccessResponse
from app.utils.http_error_response import HTTP_ERRORS
from app.core.security import get_current_user
from fastapi import status

router = APIRouter(prefix="/image", tags=["Image"])

# -------------------------------------------------------------------
# Get Gallery Images from Azure Blob Storage with pagination
# -------------------------------------------------------------------
@router.get("/template-gallery", response_model=SuccessResponse, status_code=status.HTTP_200_OK,
responses={401: HTTP_ERRORS[401], 500: HTTP_ERRORS[500]})
def get_template_gallery(
    category: str = Query(..., description="fsdu|header|footer|sidepanel|shelf|product|all"),
    search: str | None = Query(None, description="Search by image name"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at", description="created_at|image_name"),
    sort_order: str = Query("desc", description="asc|desc"),
    current_user=Depends(get_current_user)
):
    images = v1_list_images(category, search, page, page_size, sort_by, sort_order)
    return SuccessResponse(message="Gallery fetched successfully", data=images)


# -------------------------------------------------------------------
# Delete Image from Azure Blob Storage
# -------------------------------------------------------------------
@router.delete("/delete-image", response_model=SuccessResponse, status_code=status.HTTP_200_OK,
responses={401: HTTP_ERRORS[401], 500: HTTP_ERRORS[500]})
def delete_image(
    url: str = Query(..., description="Full blob URL"),
    current_user=Depends(get_current_user)
):
    result = delete_image_from_blob(url)
    deleted_meta = delete_upload_record(url)
    return SuccessResponse(
        message="Image deleted successfully",
        data={
            "blob_deleted": result,
            "db_deleted": deleted_meta
        }
    )


# -------------------------------------------------------------------
# Upload refinement image to azure Blob Storage
# -------------------------------------------------------------------
@router.post("/refinement-upload", response_model=SuccessResponse, status_code=status.HTTP_200_OK,
responses={401: HTTP_ERRORS[401], 500: HTTP_ERRORS[500]})
async def upload_refinement_image(
    project_id: str = Form(...),
    stage: str = Form(..., description="Colour_Theme|Graphics|Product_Placement"),
    image_name: str = Form(...),
    file: UploadFile = File(...),
    current_user=Depends(get_current_user)
):
   url = refinement_image_upload(project_id, image_name, file)
   save_refinement_to_cosmos(
        url=url,
        stage=stage,
        project_id=project_id
    )
   return SuccessResponse(message="Refinement Image uploaded successfully", data={"url": url})


# -------------------------------------------------------------------
# Delete refinement image from azure Blob Storage
# -------------------------------------------------------------------
@router.delete("/refinement-delete", response_model=SuccessResponse, status_code=status.HTTP_200_OK,
responses={401: HTTP_ERRORS[401], 500: HTTP_ERRORS[500]})
def delete_refinement_image(
    project_id: str,
    url: str,
    current_user=Depends(get_current_user)
):
   result = delete_refinement(project_id, url)
   return SuccessResponse(message="Image deleted successfully", data=result)


# -------------------------------------------------------------------
# Upload Image with duplicate check
# -------------------------------------------------------------------
@router.post("/image-upload", response_model=SuccessResponse, status_code=status.HTTP_200_OK,
responses={401: HTTP_ERRORS[401], 500: HTTP_ERRORS[500]})
async def upload_images(
    category: str = Form(..., description="fsdu|header|footer|sidepanel|shelf|product"),
    image_name: str = Form(...),
    action: str = Form(..., description="overwrite|keep_both"),
    file: UploadFile = File(...),
    current_user=Depends(get_current_user)
):
    file_bytes = await file.read() 
    file.file.seek(0) 
    data = upload_image_v1(file, image_name, category, action)
    thumbnail_url = create_thumbnail(file_bytes, image_name, category)
    save_upload_record(
        url=data["url"],
        image_name=data["image_name"],
        category=category,
        user_id=current_user["id"],
        thumb_url=thumbnail_url
    )
    return SuccessResponse(
        message="Image uploaded successfully",
        data={
            **data,
            "thumbnail_url": thumbnail_url
        }
    )


# -------------------------------------------------------------------
# V1- Check Image exist in Blob Storage
# -------------------------------------------------------------------
@router.post("/image-exist", response_model=SuccessResponse, status_code=status.HTTP_200_OK,
responses={401: HTTP_ERRORS[401], 500: HTTP_ERRORS[500]})
async def v1_image_exist(
    category: str = Form(..., description="fsdu|header|footer|sidepanel|shelf|product"),
    image_name: str = Form(...),
    current_user=Depends(get_current_user)
):
    result = v1_image_exist_in_blob(image_name, category)
    return SuccessResponse(message="Image checked successfully", data=result)
