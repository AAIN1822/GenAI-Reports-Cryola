from app.utils.datetime_helper import utc_unix
from app.db.db_config import IMAGES_CONTAINER
from fastapi import HTTPException
from app.db.session import get_db
from uuid import uuid4

CATEGORY_LIST = [
    "fsdu",
    "header",
    "footer",
    "sidepanel",
    "shelf",
    "product",
]

# -----------------------------------
# Save uploaded image metadata
# -----------------------------------
def save_upload_record(url: str, image_name: str, category: str, user_id: str, thumb_url: str):
    db = get_db()
    container = db[IMAGES_CONTAINER]
    category = category.lower()

    # Check for existing record (duplicate)
    query = """ SELECT * FROM c WHERE c.image_name = @image_name AND c.category = @category """
    params = [
        {"name": "@image_name", "value": image_name},
        {"name": "@category", "value": category},
    ]
    items = list(
        container.query_items(
            query=query, parameters=params, enable_cross_partition_query=True
        )
    )
    # If duplicate exists → update
    if items:
        record = items[0]
        record.update({
            "url": url,
            "thumbnail_url": thumb_url,
            "uploaded_by": user_id,
            "created_at": utc_unix()
        })
        container.replace_item(
            item=record["id"],
            body=record
        )
        return record

    # Else → create new record
    record = {
        "id": str(uuid4()),
        "url": url,
        "thumbnail_url": thumb_url,
        "image_name": image_name,
        "category": category,
        "uploaded_by": user_id,
        "created_at": utc_unix()
    }
    container.create_item(record)
    return record


# -----------------------------------
# Delete metadata by URL
# -----------------------------------
def delete_upload_record(url: str):
    db = get_db()
    container = db[IMAGES_CONTAINER]
    query = "SELECT * FROM c WHERE c.url = @url"
    items = list(container.query_items(
        query=query,
        parameters=[{"name": "@url", "value": url}],
        enable_cross_partition_query=True
    ))

    if not items:
        return None

    item = items[0]
    container.delete_item(item["id"], item["category"])
    return item


# List Images with Pagination and Search
def v1_list_images(category: str, search: str | None, page: int, page_size: int, sort_by: str, sort_order: str):
    db = get_db()
    container = db[IMAGES_CONTAINER]
    if category != "all" and category not in CATEGORY_LIST:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category '{category}'. Allowed: {CATEGORY_LIST + ['all']}"
        )

    SORT_FIELD_MAP = {
        "image_name": "c.image_name",
        "created_at": "c.created_at"
    }

    if sort_by not in SORT_FIELD_MAP:
        raise HTTPException(
            status_code=400,
            detail="Invalid sort_by. Allowed: image_name, created_at"
        )

    if sort_order not in ("asc", "desc"):
        raise HTTPException(
            status_code=400,
            detail="Invalid sort_order. Allowed: asc, desc"
        )

    offset = (page - 1) * page_size
    query_parts = [
        "SELECT c.category, c.image_name, c.url, c.thumbnail_url",
        "FROM c",
        "WHERE 1=1"
    ]

    params = []

    # Apply category filter ONLY if not 'all'
    if category != "all":
        query_parts.append("AND c.category = @cat")
        params.append({"name": "@cat", "value": category})

    # Apply search filter
    if search:
        query_parts.append(
            "AND CONTAINS(c.image_name, @search, true)"
        )
        params.append({"name": "@search", "value": search})

    query_parts.append(
        f"ORDER BY {SORT_FIELD_MAP[sort_by]} {sort_order.upper()}"
    )
    query_parts.append(f"OFFSET {offset} LIMIT {page_size}")
    data_query = " ".join(query_parts)
    items = list(container.query_items(
        query=data_query,
        parameters=params,
        enable_cross_partition_query=True
    ))
    # Get total count for pagination
    count_parts = [
        "SELECT VALUE COUNT(1)",
        "FROM c",
        "WHERE 1=1"
    ]

    if category != "all":
        count_parts.append("AND c.category = @cat")

    if search:
        count_parts.append(
            "AND CONTAINS(c.image_name, @search, true)"
        )

    count_query = " ".join(count_parts)
    total = list(container.query_items(
        query=count_query,
        parameters=params,
        enable_cross_partition_query=True
    ))[0]

    return {
        "items": items,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": (total + page_size - 1) // page_size
        }
    }
