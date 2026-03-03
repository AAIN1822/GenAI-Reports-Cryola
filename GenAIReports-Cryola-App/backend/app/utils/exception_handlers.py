"""
Custom global exception handlers for FastAPI.
Converts HTTP and unexpected server errors into a consistent JSON response format.
Ensures all exceptions return standardized ErrorResponse schema.
"""

from app.schemas.response_schema import ErrorResponse
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse

# --- Handles all HTTPExceptions (400, 401, 403, 404, 409, etc.) ---
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            status_code=exc.status_code,
            message=exc.detail or "HTTP Error",
            detail=str(exc),
        ).model_dump(),
    )

# --- Handles all unhandled Python exceptions (500s) ---
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            status_code=500,
            message="Internal Server Error",
            detail=str(exc),
        ).model_dump(),
    )