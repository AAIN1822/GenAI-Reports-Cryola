from app.schemas.project_stage_schema import ProjectStage
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class ProjectCreate(BaseModel):
    account: str = Field(..., min_length=1)
    structure: str = Field(..., min_length=1)
    sub_brand: str = Field(..., min_length=1)
    season: str = Field(..., min_length=1)
    region: str = Field(..., min_length=1)
    project_description: Optional[str] = None

class Project(BaseModel):
    id: str
    account: str
    structure: str
    sub_brand: str
    season: str
    region: str
    project_description: Optional[str] = None
    user_id: Optional[str] = None
    created_at: Optional[int] = None
    stage: ProjectStage

    model_config = ConfigDict(extra="allow")