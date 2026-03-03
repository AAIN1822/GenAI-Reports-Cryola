"""
Data models used for authentication and user management.
Contains request/response schemas for user signup, login, SSO authentication,
token response, and API error formatting.
"""

from pydantic import BaseModel, EmailStr, Field
from pydantic import ConfigDict
from datetime import datetime

#Schema for creating a new user
class UserCreateSchema(BaseModel):
    name: str = Field(..., min_length=2)
    email: EmailStr = Field(..., description='Must be a valid email address')
    password: str 
    role_id: str = Field(..., description='Must be either "admin" or "designer"')

    model_config = ConfigDict(from_attributes=True)

#Schema for user login
class UserLoginSchema(BaseModel):
    email: EmailStr = Field(..., description='Must be a valid email address')
    password: str

#Schema for login response
class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int