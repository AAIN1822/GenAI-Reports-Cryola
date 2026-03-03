from pydantic import ConfigDict, BaseModel, Field
from typing import Optional

class RoleSchema(BaseModel):
    id: str             
    role: str = Field(..., min_length=1)
    created_time: Optional[int] = None
    modified_time: Optional[int] = None

    model_config = ConfigDict(extra="allow", from_attributes=True)