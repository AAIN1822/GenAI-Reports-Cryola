import os
import uuid
from app.services.ai_integration_service import build_folder_name
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from app.db.db_config import PROJECTS_CONTAINER
from fastapi import UploadFile, HTTPException
from app.core.config import settings
from urllib.parse import urlparse
from app.db.session import get_db
from PIL import Image
import logging, io

logger = logging.getLogger("blob_service")
AZURE_STORAGE_ACCOUNT_NAME = settings.AZURE_STORAGE_ACCOUNT_NAME
AZURE_STORAGE_ACCOUNT_KEY = settings.AZURE_STORAGE_ACCOUNT_KEY
AZURE_BLOB_CONTAINER = settings.AZURE_BLOB_CONTAINER_NAME

# Allowed folders under the resource container
ALLOWED_DIRECTORIES = [
    "fsdu",
    "header",
    "footer",
    "sidepanel",
    "shelf",
    "product",
]

#credential=AZURE_STORAGE_ACCOUNT_KEY
credential = DefaultAzureCredential()

blob_service_client = BlobServiceClient(
    account_url=f"https://{AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net",
    credential=credential
)

# ----------------------------------------
# Delete Image from Azure Blob Storage
# ----------------------------------------
def delete_image_from_blob(file_url: str):
    """Delete an image from Azure Blob Storage using its full URL."""

    try:
        parsed = urlparse(file_url)
        path = parsed.path.lstrip("/")  
        parts = path.split("/", 1)
        if len(parts) != 2:
            raise HTTPException(status_code=400, detail="Invalid blob URL format")

        container_name, blob_name = parts[0], parts[1]

        # Validate container
        if container_name != AZURE_BLOB_CONTAINER:
            raise HTTPException(
                status_code=400, 
                detail="URL does not belong to the configured storage container"
            )

        blob_client = blob_service_client.get_blob_client(
            container=container_name,
            blob=blob_name
        )

        blob_client.delete_blob()

        return {"deleted": True, "blob": blob_name}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting file: {str(e)}")



# ----------------------------------------
# User refinement image upload
# ----------------------------------------
def refinement_image_upload(project_id: str, image_name: str, file: UploadFile) -> str:
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
        blob_path = f"project/{folder_name}/{image_name}"
        container_client = blob_service_client.get_container_client(AZURE_BLOB_CONTAINER)
        container_client.get_container_properties()
        blob_client = container_client.get_blob_client(blob_path)
        blob_client.upload_blob(file.file, overwrite=True)
        blob_url = (
            f"https://{AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net/"
            f"{AZURE_BLOB_CONTAINER}/{blob_path}"
        )
        return blob_url
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")
    
# -----------------------------------
# Save uploaded image metadata
# -----------------------------------
def save_refinement_to_cosmos(url: str, stage: str, project_id: str):
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
        refinement_entry = {
            "url": url,
            "stage": stage,
            }
        if "refinement_input" not in project or project["refinement_input"] is None:
            project["refinement_input"] = []

        project["refinement_input"].append(refinement_entry)
        project_container.replace_item(item=project["id"], body=project)

    except Exception as e:
        raise Exception(f"Project not found: {e}")
    

# -----------------------------------
# Delete refinement image
# -----------------------------------
def delete_refinement(project_id: str, url: str):
    db = get_db()
    project_container = db[PROJECTS_CONTAINER]
    try:
        delete_image_from_blob(url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Blob delete failed: {e}")

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
    if "refinement_input" in project and project["refinement_input"]:
        project["refinement_input"] = [
            item for item in project["refinement_input"]
            if item["url"] != url
        ]
    else:
        raise HTTPException(status_code=404, detail="No refinement entries found")

    try:
        project_container.replace_item(item=project["id"], body=project)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cosmos update failed: {e}")

    return {"message":"Refinement Image deleted successfully from Azure Blob and Cosmos DB."}
  

# upload image with duplicate handling
def upload_image_v1(file: UploadFile, image_name:str, category: str, action: str) -> dict:
    folder_name = category.lower()
    container_client = blob_service_client.get_container_client(AZURE_BLOB_CONTAINER)
    
    # Invalid retry protection
    if action not in ("overwrite", "keep_both"):
        raise HTTPException(
            status_code=400,
            detail="Invalid action. Allowed: overwrite | keep_both"
        )
    
    # Keep both - Rename file
    if action == "keep_both":
        image_name = generate_incremental_name(
            container_client=container_client,
            folder_name=folder_name,
            original_name=image_name
        )
    blob_name = f"template_gallery/{folder_name}/{image_name}"
    blob_client = container_client.get_blob_client(blob_name)
    blob_client.upload_blob(file.file, overwrite=True)
    blob_url = (
        f"https://{AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net/"
        f"{AZURE_BLOB_CONTAINER}/{blob_name}"
    )
    return {
        "image_name": image_name,
        "url": blob_url
    }

# Generate incremental name for duplicate files
def generate_incremental_name(
    container_client,
    folder_name: str,
    original_name: str
) -> str:
    name, ext = original_name.rsplit(".", 1)
    index = 1
    while True:
        new_name = f"{name}_{index}.{ext}"
        blob_path = f"template_gallery/{folder_name}/{new_name}"
        if not container_client.get_blob_client(blob_path).exists():
            return new_name
        
        index += 1


# v1_Check if image exists in blob
def v1_image_exist_in_blob(image_name: str, category: str) -> dict:
    folder_name = category.lower()
    container_client = blob_service_client.get_container_client(AZURE_BLOB_CONTAINER)
    blob_name = f"template-gallery/{folder_name}/{image_name}"
    blob_client = container_client.get_blob_client(blob_name)
    exists = blob_client.exists()
    if exists:
        url = (
            f"https://{AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net/"
            f"{AZURE_BLOB_CONTAINER}/{blob_name}"
        )
    else:
        url = ""

    return {
        "status": exists,
        "url": url
    }


# create thumbnail & upload to blob storage
def create_thumbnail(file_bytes: bytes, image_name: str, category: str, size=(300, 300)) -> str:
    image = Image.open(io.BytesIO(file_bytes))
    ext = os.path.splitext(image_name)[1].lower()
    format_map = {
        ".jpg": "JPEG",
        ".jpeg": "JPEG",
        ".png": "PNG",
        ".webp": "WEBP"
    }
    image_format = format_map.get(ext, "JPEG")

    # JPEG requires RGB mode
    if image_format == "JPEG" and image.mode in ("RGBA", "P"):
        image = image.convert("RGB")

    image.thumbnail(size)
    thumb_io = io.BytesIO()
    image.save(thumb_io, format=image_format, quality=100)
    thumb_bytes = thumb_io.getvalue()
    folder_name = category.lower()
    container_client = blob_service_client.get_container_client(AZURE_BLOB_CONTAINER)
    blob_name = f"thumbnails/{folder_name}/{image_name}"
    blob_client = container_client.get_blob_client(blob_name)
    blob_client.upload_blob(io.BytesIO(thumb_bytes), overwrite=True)
    thumb_url = (
        f"https://{AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net/"
        f"{AZURE_BLOB_CONTAINER}/{blob_name}"
    )
    return thumb_url

