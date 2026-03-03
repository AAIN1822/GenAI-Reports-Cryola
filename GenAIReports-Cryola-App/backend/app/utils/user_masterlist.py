from app.db.db_config import USER_MASTER_LIST_CONTAINER
from fastapi import HTTPException, status
from app.db.session import get_db

def validate_user_from_masterlist(email: str):
    db = get_db()
    user_masterlist = db[USER_MASTER_LIST_CONTAINER]
    email = email.strip().lower()
    try:
        query = "SELECT * FROM c WHERE c.email = @email AND c.is_active = true"
        params = [{"name": "@email", "value": email}]
        items = list(user_masterlist.query_items(
            query=query,
            parameters=params,
            enable_cross_partition_query=True
        ))

        if not items:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to access this application. Please contact your administrator for access"
            )

        return True

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Master user validation failed"
        )
