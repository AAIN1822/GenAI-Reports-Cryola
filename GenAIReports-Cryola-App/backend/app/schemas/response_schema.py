"""
Defines generic SuccessResponse and ErrorResponse schemas.
Used across the API to standardize output formatting and messaging.
"""

from pydantic import BaseModel
from typing import Optional, Any

class ErrorResponse(BaseModel):
    status_code: int
    message: str
    detail: Optional[Any] = None

class SuccessResponse(BaseModel):
    status: str = "success"
    message: str
    data: Optional[Any] = None