from app.schemas.masterdata_schema import MasterDataCreate, MdUserCreate
from app.services.masterdata_service import check_unique, create_item
from fastapi import APIRouter, HTTPException, Depends, status
from app.schemas.response_schema import SuccessResponse
from app.utils.http_error_response import HTTP_ERRORS
from app.db.db_config import (
    ACCOUNTS_CONTAINER,
    STRUCTURES_CONTAINER,
    SUBBRANDS_CONTAINER,
    REGIONS_CONTAINER,
    SEASONS_CONTAINER,
    DISPLAY_DIMENSIONS_CONTAINER,
    PRODUCT_DIMENSIONS_CONTAINER,
    USER_MASTER_LIST_CONTAINER,
)
from app.core.security import get_current_user
from app.utils.datetime_helper import utc_unix
from app.db.session import get_db
from uuid import uuid4

router = APIRouter()

ENTITY_NAMES = [
    ACCOUNTS_CONTAINER,
    STRUCTURES_CONTAINER,
    SUBBRANDS_CONTAINER,
    REGIONS_CONTAINER,
    SEASONS_CONTAINER,
    DISPLAY_DIMENSIONS_CONTAINER,
    PRODUCT_DIMENSIONS_CONTAINER,
]

def create_router(entity_name: str):
    entity_router = APIRouter(
        prefix=f"/master/{entity_name}",
        tags=["Master Data"],
        dependencies=[Depends(get_current_user)]
    )
    
    def get_container():
        db = get_db()
        try:
            return db[entity_name]
        except KeyError:
            raise HTTPException(
                status_code=500,
                detail=f"Container for entity '{entity_name}' not found"
            )

    # ───────────────────────────────────────────────
    # LIST ITEMS
    # ───────────────────────────────────────────────
    @entity_router.get("", response_model=SuccessResponse, responses={401: HTTP_ERRORS[401]})
    def list_items():
        container = get_container()
        query = "SELECT * FROM c"
        items = list(container.query_items(query=query, enable_cross_partition_query=True))
        result = [
            {
                "id": i.get("id"),
                "name": i.get("name"),
                "created_by": i.get("created_by")
            }
            for i in items
        ]

        return SuccessResponse(
            message=f"{entity_name} fetched successfully",
            data={
                "total": len(result),
                "items": result
            }
        )

    # ───────────────────────────────────────────────
    # ADD ITEM
    # ───────────────────────────────────────────────
    @entity_router.post(
        "",
        response_model=SuccessResponse,
        status_code=status.HTTP_200_OK,
        responses={401: HTTP_ERRORS[401], 409: HTTP_ERRORS[409]}
    )
    def create_master_data(payload: MasterDataCreate, current_user=Depends(get_current_user)):
        container = get_container()
        if not check_unique(container, payload.name):
            raise HTTPException(status_code=409, detail=f"{entity_name} name already exists")

        data = payload.model_dump()
        data["created_by"] = current_user["id"]
        obj = create_item(container, data)
        return SuccessResponse(
            message=f"{entity_name} created successfully",
            data=obj
        )

    # ───────────────────────────────────────────────
    # DELETE ITEM
    # ───────────────────────────────────────────────
    @entity_router.delete(
        "/{item_id}",
        response_model=SuccessResponse,
        responses={401: HTTP_ERRORS[401], 403: HTTP_ERRORS[403], 404: HTTP_ERRORS[404]},
    )
    def delete_master_data(item_id: str, current_user=Depends(get_current_user)):
        container = get_container()
        query = "SELECT * FROM c WHERE c.id = @id"
        params = [{"name": "@id", "value": item_id}]
        
        items = list(container.query_items(
            query=query,
            parameters=params,
            enable_cross_partition_query=True
        ))

        if not items:
            raise HTTPException(status_code=404, detail=f"{item_id} not found")

        item = items[0]
        # Permission check
        if item.get("created_by") != current_user["id"]:
            raise HTTPException(
                status_code=403,
                detail="You can delete only the items created by you"
            )

        container.delete_item(item["id"], partition_key=item["id"])

        return SuccessResponse(
            message=f"{entity_name} deleted successfully",
            data={"id": item_id}
        )

    return entity_router


# Register routers dynamically
for entity in ENTITY_NAMES:
    router.include_router(create_router(entity))


#-------------------------------------------------
# List MD Users 
#-------------------------------------------------
@router.get("/master/list-user",response_model=SuccessResponse, status_code=status.HTTP_200_OK, 
tags=["Master Data"], responses={401: HTTP_ERRORS[401], 500: HTTP_ERRORS[500]})
def list_users(current_user=Depends(get_current_user)):
    db = get_db()
    container = db[USER_MASTER_LIST_CONTAINER]
    query = "SELECT c.id, c.email, c.name, c.is_active FROM c"
    items = list(container.query_items(
        query=query,
        enable_cross_partition_query=True
    ))
    result = [
        {
            "email": i["email"],
            "name": i.get("name", ""),
            "is_active": i.get("is_active", False)
        }
        for i in items
    ]

    return SuccessResponse(
        message="MD user list fetched successfully",
        data={
            "total": len(result),
            "items": result
        }
    )


#-------------------------------------------------
# Add MD User 
#-------------------------------------------------
@router.post("/master/add-user", response_model=SuccessResponse, status_code=status.HTTP_200_OK, 
tags=["Master Data"], responses={401: HTTP_ERRORS[401], 409: HTTP_ERRORS[409]})
def create_user(
    payload: MdUserCreate,
    current_user=Depends(get_current_user)
):
    db = get_db()
    container = db[USER_MASTER_LIST_CONTAINER]
    email = payload.email.lower()
    name = payload.name.lower()
    # Check if already exists
    try:
        container.read_item(item=email, partition_key=email)
        
    except Exception:
        pass

    else:
        raise HTTPException(
            status_code=409,
            detail="User already exists in Master List"
        )

    data = {
        "id": str(uuid4()),
        "email": email,
        "name": name,
        "is_active": payload.is_active,
        "created_at": utc_unix()
    }
    container.create_item(body=data)
    return SuccessResponse(
        message="User Added to Master List successfully",
        data={
            "id": data["id"],
            "email": email,
            "name": name,
            "is_active": payload.is_active
        }
    )



#-------------------------------------------------
# Delete MD User
#-------------------------------------------------
@router.delete("/master/delete-user/{email}", response_model=SuccessResponse, status_code=status.HTTP_200_OK,
tags=["Master Data"], responses={401: HTTP_ERRORS[401], 404: HTTP_ERRORS[404]})
def delete_md_user(
    email: str,
    current_user=Depends(get_current_user)
):
    db = get_db()
    container = db[USER_MASTER_LIST_CONTAINER]
    email = email.lower()
    try:
        container.delete_item(item=email, partition_key=email)
    except Exception:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    return SuccessResponse(
        message="User deleted successfully",
        data={"email": email}
    )
