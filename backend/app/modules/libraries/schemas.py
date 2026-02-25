from pydantic import BaseModel
from typing import Optional

class LibraryCreateRequest(BaseModel):
    name: str
    industry: str
    description: str = ""
    is_global: Optional[bool] = False
    
class LibraryResponse(BaseModel):
    name: str
    industry: str
    description: str = ""
    is_global: Optional[bool] = False
    
    class Config:
        from_attributes = True