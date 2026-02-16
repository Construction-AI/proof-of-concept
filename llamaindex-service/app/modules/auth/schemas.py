from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str
    
class TokenData(BaseModel):
    id: Optional[str] = None

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    
    first_name: str
    last_name: str
    
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    created_at: datetime
    last_modified: datetime
    
    class Config:
        from_attributes = True