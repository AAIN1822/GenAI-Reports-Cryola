from pydantic import BaseModel, EmailStr, ConfigDict

class OtpSchema(BaseModel):
    id: str
    email: EmailStr
    otp: str
    used: bool
    expires_at: str
    created_at: int 

    model_config = ConfigDict(extra="allow", from_attributes=True)