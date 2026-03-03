from pydantic import ConfigDict, BaseModel
from typing import Optional

class ActivityLog(BaseModel):
    id: str
    user_id: str
    login_time: Optional[int] = None
    logout_time: Optional[int] = None

    model_config = ConfigDict(extra="allow", from_attributes=True)