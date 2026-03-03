from app.services.compression_helper import copy_blob_with_compression_if_needed
from app.services.ai_integration_service import build_folder_name
from app.services.project_service import extract_image_urls
from app.schemas.project_stage_schema import ProjectStage
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from app.db.db_config import PROJECTS_CONTAINER
from app.core.config import settings
from app.db.session import get_db
from urllib.parse import urlparse
import requests, tempfile, os

# -----------------------------
# List Images from Acquia DAM
# -----------------------------
def list_images(search: str | None, page: int, page_size: int):
    base_url = settings.DAM_BASE_URL
    auth_key = settings.DAM_AUTH_KEY
    params = {
        "limit": page_size,
        "offset": (page - 1) * page_size,
        "expand": "thumbnails,file_properties"
    }
    if search:
        params["query"] = search

    response = requests.get(
        f"{base_url}/v2/assets/search",
        headers={"Authorization": f"Bearer {auth_key}"},
        params=params,
        timeout=10
    )
    response.raise_for_status()
    return response.json()


# -----------------------------
# URL TYPE CHECKS
# -----------------------------
def is_azure_blob_url(url: str) -> bool:
    return bool(url) and "blob.core.windows.net" in url

def is_dam_url(url: str) -> bool:
    return bool(url) and (
        "widencdn.net" in url or
        "widencollective.com" in url
    )


# -----------------------------
# AZURE BLOB UPLOAD
# -----------------------------
AZURE_STORAGE_ACCOUNT_NAME = settings.AZURE_STORAGE_ACCOUNT_NAME
AZURE_STORAGE_ACCOUNT_KEY = settings.AZURE_STORAGE_ACCOUNT_KEY
AZURE_BLOB_CONTAINER = settings.AZURE_BLOB_CONTAINER_NAME
#credential=AZURE_STORAGE_ACCOUNT_KEY
credential = DefaultAzureCredential()
blob_service_client = BlobServiceClient(
    account_url=f"https://{AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net",
    credential=credential
)

def stream_dam_to_blob(url: str, folder_name: str) -> str:
    response = requests.get(url, stream=True, timeout=20)
    response.raise_for_status()
    filename = os.path.basename(urlparse(url).path)
    blob_path = f"project/{folder_name}/{filename}.jpg"
    blob_client = blob_service_client.get_blob_client(container=AZURE_BLOB_CONTAINER, blob=blob_path)
    blob_client.upload_blob(
        response.raw,
        overwrite=True
    )
    return blob_client.url


# -----------------------------
# MAIN IMAGE PROCESSOR
# -----------------------------
def process_image_url(url: str, folder_name: str) -> str:
    if not url:
        return url

    # Azure Blob → Azure Blob
    if is_azure_blob_url(url):
        return copy_blob_with_compression_if_needed(url, folder_name)

    # DAM → Stream → Blob (NO local disk)
    if is_dam_url(url):
        return stream_dam_to_blob(url, folder_name)

    return url


# ----------------------------
# PAYLOAD URL HANDLING
# ----------------------------
def replace_urls_in_payload(payload: dict, url_map: dict):
    def walk(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == "image" and v in url_map:
                    obj[k] = url_map[v]
                else:
                    walk(v)
        elif isinstance(obj, list):
            for item in obj:
                walk(item)

    walk(payload)


# -----------------------------
# MAIN SERVICE FUNCTION
# -----------------------------
def update_project_details(project_id: str, payload: dict, current_user: dict):
    db = get_db()
    container = db[PROJECTS_CONTAINER]
    query = f"SELECT * FROM c WHERE c.id = '{project_id}'"
    items = list(container.query_items(query, enable_cross_partition_query=True))
    if not items:
        raise Exception("Project not found")

    project = items[0]
    pk_value = project["account"]

    if project["user_id"] != current_user["id"]:
        raise Exception("You are not authorized to update this project")

    folder_name = build_folder_name(project)
    urls = extract_image_urls(payload)
    url_map = {}
    for u in urls:
        try:
            url_map[u] = process_image_url(u, folder_name)
        except Exception:
            pass

    replace_urls_in_payload(payload, url_map)
    project["details"] = payload

    # Stage transition
    if project.get("stage") == ProjectStage.STAGE_1:
        project["stage"] = ProjectStage.STAGE_2

    # Remove Cosmos system fields
    for f in ["_etag", "_rid", "_self", "_attachments", "_ts"]:
        project.pop(f, None)

    return container.replace_item(project_id, project, pk_value)
