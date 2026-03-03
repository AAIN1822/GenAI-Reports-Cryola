from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class MasterDataCreate(BaseModel):
    name: str = Field(..., min_length=1)
    active: Optional[bool] = True

class MdUserCreate(BaseModel):
    email: EmailStr
    name: str
    is_active: bool = True