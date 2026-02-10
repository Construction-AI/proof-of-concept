from datetime import datetime
from pydantic import BaseModel
from typing import Optional

from app.modules.auth.schemas import UserResponse
from app.modules.projects.schemas import ProjectResponse

class DocumentCreate(BaseModel):
    title: str
    description: Optional[str] = None
    project_id: int
    file_url: str
    
class DocumentResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    file_url: str
    created_at: datetime
    last_modified: datetime
    
    owner: UserResponse
    project: ProjectResponse
    
    class Config:
        from_attributes = True