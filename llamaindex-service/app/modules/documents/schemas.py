from datetime import datetime
from pydantic import BaseModel

from app.modules.auth.schemas import UserResponse
from app.modules.projects.schemas import ProjectResponse

class DocumentCreate(BaseModel):
    project_id: int
    
class DocumentGetDownloadUrl(BaseModel):
    document_id: int
    
class DocumentResponse(BaseModel):
    id: int
    file_name: str
    file_storage_key: str
    content_type: str
    size: int
    created_at: datetime
    last_modified: datetime
    
    owner: UserResponse
    project: ProjectResponse
    
    class Config:
        from_attributes = True
