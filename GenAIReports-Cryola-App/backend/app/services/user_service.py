from app.core.security import hash_password, verify_password
from app.utils.datetime_helper import utc_unix
from app.db.db_config import USER_CONTAINER
from fastapi import HTTPException, status
from app.db.session import get_db

def handle_change_password(old_password:str, new_password:str, current_user:dict):
    # If SSO user, prevent password change
        if current_user["login_type"] == "sso":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="SSO users cannot change password"
            )

        # Verify old password
        if not verify_password(old_password, current_user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Old password is incorrect"
            )

        # Update user's password
        current_user["hashed_password"] = hash_password(new_password)
        current_user["modified_time"] = utc_unix()
        db = get_db()
        users_container = db[USER_CONTAINER]
        users_container.replace_item(current_user["id"], current_user)