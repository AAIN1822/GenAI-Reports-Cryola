"""
Authentication router (Cosmos DB version).
Handles register, login, OTP, reset password, refresh token, logout.
"""

from app.services.auth_service import register_user, authenticate_user, handle_forgot_password, handle_validate_otp, handle_resend_otp, handle_reset_password, handle_logout, handle_refresh_token
from app.core.security import get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
from fastapi import APIRouter, Depends, Body, BackgroundTasks, status
from app.schemas.user_schema import UserCreateSchema, UserLoginSchema
from app.utils.user_masterlist import validate_user_from_masterlist
from app.schemas.response_schema import SuccessResponse
from app.utils.http_error_response import HTTP_ERRORS

# -------------------------------------------------------------------
# Router setup
# -------------------------------------------------------------------
router = APIRouter(prefix="/auth", tags=["Authentication"])

# -------------------------------------------------------------------
# Register User
# -------------------------------------------------------------------
@router.post("/register", response_model=SuccessResponse, status_code=status.HTTP_200_OK,
    responses={400: HTTP_ERRORS[400], 409: HTTP_ERRORS[409], 500: HTTP_ERRORS[500]},
)
def register(user: UserCreateSchema):
    user.email = user.email.strip().lower()
    validate_user_from_masterlist(user.email)
    register_user(user)
    login_input = UserLoginSchema(email=user.email, password=user.password)
    tokens = authenticate_user(login_input)
    return SuccessResponse(
        message="User registered and logged in successfully",
        data=tokens
    )


# -------------------------------------------------------------------
# Login User
# -------------------------------------------------------------------
@router.post("/login", response_model=SuccessResponse, status_code=status.HTTP_200_OK,
    responses={400: HTTP_ERRORS[400], 500: HTTP_ERRORS[500]},
)
def login(user: UserLoginSchema):
    user.email = user.email.strip().lower()
    validate_user_from_masterlist(user.email)
    token = authenticate_user(user)
    return SuccessResponse(
        message="User logged in successfully",
        data=token
    )


# -------------------------------------------------------------------
# Forgot Password (send OTP)
# -------------------------------------------------------------------
@router.post("/forgot-password", response_model=SuccessResponse, status_code=status.HTTP_200_OK,
    responses={404: HTTP_ERRORS[404], 429: HTTP_ERRORS[429], 500: HTTP_ERRORS[500]},
)
async def forgot_password(
    background_tasks: BackgroundTasks,
    email: str = Body(..., embed=True),
):
    email = email.strip().lower()
    validate_user_from_masterlist(email)
    handle_forgot_password(email, background_tasks)
    return SuccessResponse(message="OTP sent successfully")


# -------------------------------------------------------------------
# Validate OTP (return password-reset token)
# -------------------------------------------------------------------
@router.post("/validate-otp", response_model=SuccessResponse,
    responses={400: HTTP_ERRORS[400], 404: HTTP_ERRORS[404]},
)
def validate_otp(
    email: str = Body(...),
    otp: str = Body(...),
):
    reset_token = handle_validate_otp(email, otp)
    return SuccessResponse(
        message="OTP is valid",
        data={"password_reset_token": reset_token}
    )


# -------------------------------------------------------------------
# Resend OTP (Cosmos DB version)
# -------------------------------------------------------------------
@router.post("/resend-otp", response_model=SuccessResponse, status_code=status.HTTP_200_OK,
    responses={404: HTTP_ERRORS[404], 429: HTTP_ERRORS[429], 500: HTTP_ERRORS[500]},
)
async def resend_otp(
    background_tasks: BackgroundTasks,
    email: str = Body(..., embed=True),
):
    handle_resend_otp(email, background_tasks)
    return SuccessResponse(message="New OTP sent successfully")


# -------------------------------------------------------------------
# Reset Password
# -------------------------------------------------------------------
@router.post("/reset-password", response_model=SuccessResponse,
    responses={401: HTTP_ERRORS[401], 404: HTTP_ERRORS[404]},
)
def reset_password(
    new_password: str = Body(...),
    password_reset_token: str = Body(...),
):
    handle_reset_password(new_password, password_reset_token)
    return SuccessResponse(message="Password reset successful")


# -------------------------------------------------------------------
# Logout
# -------------------------------------------------------------------
@router.get("/logout", response_model=SuccessResponse, status_code=status.HTTP_200_OK,
    responses={401: HTTP_ERRORS[401]},
)
def logout(current_user = Depends(get_current_user)):
    handle_logout(current_user)
    return SuccessResponse(message="Logged out successfully")


# -------------------------------------------------------------------
# Refresh Access Token
# -------------------------------------------------------------------
@router.post("/refresh", response_model=SuccessResponse, status_code=status.HTTP_200_OK)
def refresh_access_token(refresh_token: str = Body(..., embed=True)):
    new_access_token = handle_refresh_token(refresh_token)
    return SuccessResponse(
        message="Access token refreshed successfully",
        data={
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES
        }
    )