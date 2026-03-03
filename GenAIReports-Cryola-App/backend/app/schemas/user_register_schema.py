from pydantic import BaseModel, EmailStr, ConfigDict, Field
from typing import Optional

class UserCreate(BaseModel):
    id: str = Field(..., min_length=5)
    name: str = Field(..., min_length=2)
    email: EmailStr
    hashed_password: Optional[str] = None
    role_id: str = Field(..., min_length=3)
    status: str
    login_type: str
    created_time: Optional[int] = None
    modified_time: Optional[int] = None
    last_login_time: Optional[int] = None

    model_config = ConfigDict(extra="allow", from_attributes=True)