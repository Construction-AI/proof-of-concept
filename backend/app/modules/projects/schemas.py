from datetime import datetime
from pydantic import BaseModel
from typing import Optional

from app.modules.auth.schemas import UserResponse

class ProjectCreate(BaseModel):
    title: str
    description: Optional[str] = None
    
class ProjectResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    created_at: datetime
    last_modified: datetime
    
    owner: UserResponse
    
    class Config:
        from_attributes = True