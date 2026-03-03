"""
User router: Cosmos DB Core API (NoSQL)
Handles user-specific operations like fetching profile and changing password.
"""

from fastapi import APIRouter, Depends, HTTPException, Body, status
from app.services.user_service import handle_change_password
from app.schemas.response_schema import SuccessResponse
from app.schemas.user_return_schema import UserReturn
from app.utils.http_error_response import HTTP_ERRORS
from app.core.security import get_current_user

router = APIRouter(prefix="/user", tags=["User"])


# -------------------------------------------------------------------
# Get Current User Profile
# -------------------------------------------------------------------
@router.get("/me", response_model=SuccessResponse, status_code=status.HTTP_200_OK,
    responses={401: HTTP_ERRORS[401], 404: HTTP_ERRORS[404]},
)
def get_current_user_profile(current_user=Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")

    user_public = UserReturn(
        id=current_user["id"],
        name=current_user["name"],
        email=current_user["email"],
        role_id=current_user["role_id"],
        login_type=current_user["login_type"],
        last_login_time=current_user["last_login_time"],)

    return SuccessResponse(
        message="User details fetched successfully",
        data=user_public
    )


# -------------------------------------------------------------------
# Change Password
# -------------------------------------------------------------------
@router.post("/change-password", response_model=SuccessResponse, status_code=status.HTTP_200_OK,
    responses={401: HTTP_ERRORS[401]},
)
def change_password(
    old_password: str = Body(...),
    new_password: str = Body(...),
    current_user=Depends(get_current_user)
):
    try:
        handle_change_password(old_password, new_password, current_user)
        return SuccessResponse(
            message="Password changed successfully"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Password update failed: {str(e)}"
        )