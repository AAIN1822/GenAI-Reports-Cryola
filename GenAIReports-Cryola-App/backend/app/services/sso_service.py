from app.core.security import create_access_token, create_refresh_token
from app.utils.user_masterlist import validate_user_from_masterlist
from app.db.db_config import USER_CONTAINER, ACTIVITY_CONTAINER
from app.schemas.user_register_schema import UserCreate
from app.schemas.activity_schema import ActivityLog
from app.services.sso_helper import verify_ms_id_token
from app.utils.datetime_helper import utc_unix
from app.db.session import get_db
from fastapi import HTTPException
from uuid import uuid4

def handle_sso_login(id_token: str, role_id: str) -> tuple[str, str]:
    # Verify Microsoft ID token
        payload = verify_ms_id_token(id_token)
        db = get_db()
        user_container = db[USER_CONTAINER]
        activity_container = db[ACTIVITY_CONTAINER]

        email = payload.get("preferred_username") or payload.get("email")
        if isinstance(email, bytes):
            email = email.decode("utf-8")
        if not email:
            raise HTTPException(status_code=400, detail="Email not present in ID token")
        email = email.strip().lower()

        full_name = payload.get("name", "")

        #check user_masterlist
        validate_user_from_masterlist(email)
        # Check if user exists
        query = "SELECT * FROM c WHERE c.email = @email"
        params = [{"name": "@email", "value": email}]
        items = list(user_container.query_items(query=query, parameters=params, enable_cross_partition_query=True))

        if items:
            user_dict = items[0]
            # Update last login and login type
            user_dict["last_login_time"] = utc_unix()
            user_dict["login_type"] = "SSO"
            user = UserCreate(**user_dict)
        else:
            # Create new user doc
            user = UserCreate(
                id=str(uuid4()),
                name=full_name,
                email=email,
                role_id=role_id,
                status="ACTIVE",
                login_type="SSO",
                created_time=utc_unix(),
                modified_time=utc_unix(),
                last_login_time=utc_unix(),
            )

        # Upsert user to Cosmos DB
        user_container.upsert_item(body=user.model_dump())

        # Generate JWT tokens using attribute access
        access_token = create_access_token({"sub": user.email})
        refresh_token = create_refresh_token({"sub": user.email})

        # Log user activity
        activity_log = ActivityLog(
            id=str(uuid4()),
            user_id=user.id,
            login_time=utc_unix(),
            logout_time=None,
        )
        activity_container.create_item(body=activity_log.model_dump())
        return access_token, refresh_token