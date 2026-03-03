from app.services.compression_helper import copy_blob_with_compression_if_needed
from app.services.ai_integration_service import build_folder_name
from app.schemas.project_stage_schema import ProjectStage
from app.schemas.project_schema import ProjectCreate
from azure.identity import DefaultAzureCredential
from app.utils.replace_paths import replace_paths
from azure.storage.blob import BlobServiceClient
from app.db.db_config import PROJECTS_CONTAINER
from fastapi.responses import StreamingResponse
from app.schemas.project_schema import Project
from app.utils.datetime_helper import utc_unix
from app.utils.copy_blobs import copy_folder
from app.core.config import settings
from app.db.session import get_db
from fastapi import HTTPException
from urllib.parse import urlparse
from typing import List
from uuid import uuid4
from io import BytesIO
import zipfile
import os

# ----------------------
# Create New Project
# ----------------------
def create_project(payload: ProjectCreate, current_user) -> Project:
    db = get_db()
    container = db[PROJECTS_CONTAINER]

    project_data = Project(
        id= str(uuid4()),
        account= payload.account,
        structure= payload.structure,
        sub_brand= payload.sub_brand,
        season= payload.season,
        region= payload.region,
        project_description= payload.project_description,
        user_id=current_user["id"],
        created_at= utc_unix(),
        stage=ProjectStage.STAGE_1,
    )

    container.create_item(body=project_data.model_dump())
    return project_data


# -----------------------
# Update Project Details
# -----------------------
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
            new_url = copy_blob_with_compression_if_needed(u, folder_name)
            url_map[u] = new_url
        except Exception:
            pass  # keep original URL if something fails

    # Replace URLs in payload
    def replace_urls(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == "image" and v in url_map:
                    obj[k] = url_map[v]
                else:
                    replace_urls(v)
        elif isinstance(obj, list):
            for item in obj:
                replace_urls(item)

    replace_urls(payload)
    project["details"] = payload

    # Stage transition
    current_stage = project.get("stage")
    if current_stage == ProjectStage.STAGE_1:
        project["stage"] = ProjectStage.STAGE_2
  
    # Remove system fields
    for f in ["_etag", "_rid", "_self", "_attachments", "_ts"]:
        project.pop(f, None)

    updated = container.replace_item(project_id, project, pk_value)
    return updated

# -----------------------
# Fetch Project By ID
# -----------------------
def fetch_project_by_id(project_id: str, current_user: dict):
    db = get_db()
    container = db[PROJECTS_CONTAINER]
    query = """
    SELECT * FROM c
    WHERE c.id = @id AND c.user_id = @user_id
    """
    items = list(
        container.query_items(
            query=query,
            parameters=[
                {"name": "@id", "value": project_id},
                {"name": "@user_id", "value": current_user["id"]},
            ],
            enable_cross_partition_query=True,
        )
    )
    if not items:
        raise Exception("Project not found")

    return items[0]


# -----------------------
# Save as new project
# -----------------------
def save_as(original_project_id: str, payload: ProjectCreate, current_user):
    db = get_db()
    project_container = db[PROJECTS_CONTAINER]
    query = "SELECT * FROM c WHERE c.id = @id"
    params = [{"name": "@id", "value": original_project_id}]
    new_project_id = str(uuid4())
    project_data = payload.model_dump()
    project_data["id"] = new_project_id
 
    new_folder_name = build_folder_name(project_data)
   
    results = list(project_container.query_items(
        query=query,
        parameters=params,
        enable_cross_partition_query=True
    ))
    if not results:
        raise HTTPException(status_code=404, detail="Project not found")
   
    original = results[0]
    old_folder_name = build_folder_name(original)
 
    old_folder = f"project/{old_folder_name}/"
    new_folder = f"project/{new_folder_name}/"
 
    # COPY BLOBS
    copied_files = copy_folder(old_folder, new_folder)
 
    new_project = {
        "id": new_project_id,
        "account": payload.account,
        "structure": payload.structure,
        "sub_brand": payload.sub_brand,
        "season": payload.season,
        "region": payload.region,
        "project_description": payload.project_description,
        "user_id": current_user["id"],
        "created_at": utc_unix(),
        "stage": original.get("stage"),
        "details": replace_paths(
            original.get("details", {}),
            old_folder,
            new_folder
        ),
        "ai_colour_theme_results": replace_paths(
            original.get("ai_colour_theme_results", []),
            old_folder,
            new_folder
        ),
        "ai_colour_theme_refinement": replace_paths(
            original.get("ai_colour_theme_refinement", []),
            old_folder,
            new_folder
        ),
        "ai_graphics_input": replace_paths(
            original.get("ai_graphics_input", ""),
            old_folder,
            new_folder
        ),
        "ai_graphics_results": replace_paths(
            original.get("ai_graphics_results", []),
            old_folder,
            new_folder
        ),
        "ai_graphics_refinement_input": replace_paths(
            original.get("ai_graphics_refinement_input", ""),
            old_folder,
            new_folder
        ),
        "ai_graphics_refinement": replace_paths(
            original.get("ai_graphics_refinement", []),
            old_folder,
            new_folder
        ),
        "ai_product_placement_input": replace_paths(
            original.get("ai_product_placement_input", ""),
            old_folder,
            new_folder
        ),
        "ai_product_placement_results": replace_paths(
            original.get("ai_product_placement_results", []),
            old_folder,
            new_folder
        ),
        "ai_product_placement_refinement_input": replace_paths(
            original.get("ai_product_placement_refinement_input", ""),
            old_folder,
            new_folder
        ),
        "ai_product_placement_refinement": replace_paths(
            original.get("ai_product_placement_refinement", []),
            old_folder,
            new_folder
        ),
        "ai_multi_angle_view_input": replace_paths(
            original.get("ai_multi_angle_view_input", ""),
            old_folder,
            new_folder
        ),
        "ai_multi_angle_view_results": replace_paths(
            original.get("ai_multi_angle_view_results", []),
            old_folder,
            new_folder
        ),
    }
    project_container.create_item(body=new_project)
    return new_project


# extract image URLs from project containers
def extract_image_urls(data):
    urls = set()   # avoid duplicates

    def walk(node):
        if isinstance(node, dict):
            for k, v in node.items():
                if k == "image" and isinstance(v, str) and v.strip():
                    urls.add(v)
                walk(v)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(data)
    return list(urls)


# download project files from blob storage
def download_project(project_id: str, current_user):
    db = get_db()
    project_container = db[PROJECTS_CONTAINER]
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
    if project["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=403,
            detail="You can only download projects created by you"
        )
    folder_name = build_folder_name(project)
    AZURE_STORAGE_ACCOUNT_NAME = settings.AZURE_STORAGE_ACCOUNT_NAME
    AZURE_STORAGE_ACCOUNT_KEY = settings.AZURE_STORAGE_ACCOUNT_KEY
    #credential=AZURE_STORAGE_ACCOUNT_KEY
    credential = DefaultAzureCredential()

    blob_service_client = BlobServiceClient(
        account_url=f"https://{AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net",
        credential=credential
   )
    blob_urls = extract_blob_urls(project)
    if not blob_urls:
        raise HTTPException(
            status_code=404,
            detail="No files referenced in project"
        )
    blob_urls = list(set(blob_urls))
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for blob_url in blob_urls:
            parsed = urlparse(blob_url)
            path_parts = parsed.path.lstrip("/").split("/", 1)
            container_name = path_parts[0]
            blob_name = path_parts[1]
            blob_client = blob_service_client.get_blob_client(
                container=container_name,
                blob=blob_name
            )
            try:
                file_bytes = blob_client.download_blob().readall()
            except Exception:
                continue

            zip_file.writestr(
                blob_name.split("/", 1)[-1],
                file_bytes
            )
    zip_buffer.seek(0)
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename={folder_name}.zip"
        }
    )

# Extract Azure Blob URLs from cosmo db project
def extract_blob_urls(obj) -> List[str]:
    urls = []
    if isinstance(obj, dict):
        for v in obj.values():
            urls.extend(extract_blob_urls(v))

    elif isinstance(obj, list):
        for item in obj:
            urls.extend(extract_blob_urls(item))

    elif isinstance(obj, str):
        if ".blob.core.windows.net/" in obj:
            urls.append(obj)

    return urls


# List projects with pagnation
def v1_fetch_all_projects(search: str | None, filters: dict, page: int, page_size: int, sort_by: str, sort_order: str, current_user):
    db = get_db()
    container = db[PROJECTS_CONTAINER]

    SORT_FIELD_MAP = {
        "account": "c.account",
        "structure": "c.structure",
        "sub_brand": "c.sub_brand",
        "season": "c.season",
        "region": "c.region",
        "project_description": "c.project_description",
        "created_at": "c.created_at",
    }

    if sort_by not in SORT_FIELD_MAP:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sort_by. Allowed: {list(SORT_FIELD_MAP.keys())}"
        )

    if sort_order not in ("asc", "desc"):
        raise HTTPException(
            status_code=400,
            detail="Invalid sort_order. Allowed: asc, desc"
        )

    offset = (page - 1) * page_size
    query_parts = [
        """
        SELECT c.id, c.account, c.structure, c.sub_brand, c.season,
               c.region, c.project_description,
               c.user_id, c.created_at
        FROM c
        WHERE c.user_id = @user_id
        """
    ]

    params = [{"name": "@user_id", "value": current_user["id"]}]

    # filter conditions
    FILTER_FIELD_MAP = {
        "account": "c.account",
        "structure": "c.structure",
        "sub_brand": "c.sub_brand",
        "season": "c.season",
        "region": "c.region",
    }
    for key, value in filters.items():
        if value:
            query_parts.append(f"AND {FILTER_FIELD_MAP[key]} = @{key}")
            params.append({"name": f"@{key}", "value": value})

    # Search filter
    if search:
        query_parts.append("""
            AND (
                CONTAINS(c.account, @search, true)
                OR CONTAINS(c.structure, @search, true)
                OR CONTAINS(c.sub_brand, @search, true)
                OR CONTAINS(c.season, @search, true)
                OR CONTAINS(c.region, @search, true)
                OR CONTAINS(c.project_description, @search, true)
            )
        """)
        params.append({"name": "@search", "value": search})

    # Sorting
    query_parts.append(
        f"ORDER BY {SORT_FIELD_MAP[sort_by]} {sort_order.upper()}"
    )

    # Pagination
    query_parts.append(f"OFFSET {offset} LIMIT {page_size}")

    data_query = " ".join(query_parts)

    items = list(
        container.query_items(
            query=data_query,
            parameters=params,
            enable_cross_partition_query=True,
        )
    )
    # Total count
    count_parts = [
        """
        SELECT VALUE COUNT(1)
        FROM c
        WHERE c.user_id = @user_id
        """
    ]

    for key, value in filters.items():
        if value:
            count_parts.append(f"AND {FILTER_FIELD_MAP[key]} = @{key}")

    if search:
        count_parts.append("""
            AND (
                CONTAINS(c.account, @search, true)
                OR CONTAINS(c.structure, @search, true)
                OR CONTAINS(c.sub_brand, @search, true)
                OR CONTAINS(c.season, @search, true)
                OR CONTAINS(c.region, @search, true)
                OR CONTAINS(c.project_description, @search, true)
            )
        """)

    count_query = " ".join(count_parts)
    total = list(
        container.query_items(
            query=count_query,
            parameters=params,
            enable_cross_partition_query=True,
        )
    )[0]

    return {
        "projects": items,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": (total + page_size - 1) // page_size
        }
    }
