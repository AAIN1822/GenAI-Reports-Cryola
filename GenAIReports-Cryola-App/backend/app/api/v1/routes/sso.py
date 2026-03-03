"""
Authenticates a user via Microsoft SSO. Validates the ID token, retrieves or
creates the user record in Cosmos DB (Core API NoSQL), records login activity,
and returns JWT tokens.
"""

from fastapi import APIRouter, Body, HTTPException, status
from app.core.security import  ACCESS_TOKEN_EXPIRE_MINUTES
from app.schemas.response_schema import SuccessResponse
from app.services.sso_service import handle_sso_login
from app.utils.http_error_response import HTTP_ERRORS
from app.schemas.user_schema import LoginResponse

router = APIRouter(prefix="/auth/sso", tags=["SSO"])

@router.post(
    "/login",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
    responses={400: HTTP_ERRORS[400], 401: HTTP_ERRORS[401], 404: HTTP_ERRORS[404], 500: HTTP_ERRORS[500]},
)
def sso_login(id_token: str = Body(..., embed=True),
              role_id: str = Body(..., description='Must be either "admin" or "designer"')):
    try:
        access_token, refresh_token = handle_sso_login(id_token, role_id)        
        return SuccessResponse(
            message="SSO login successful",
            data=LoginResponse(
                access_token = access_token,
                refresh_token = refresh_token,
                token_type = "bearer",
                expires_in = ACCESS_TOKEN_EXPIRE_MINUTES,
            ),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )