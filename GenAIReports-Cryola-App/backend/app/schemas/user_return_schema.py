from pydantic import BaseModel

class UserReturn(BaseModel):
    id: str
    name: str
    email: str
    role_id: str
    login_type: str
    last_login_time: int | None = None