from pydantic import BaseModel
from typing import  List

class ChatCreateRequest(BaseModel):
    title: str
        
class MessageResponse(BaseModel):
    id: int
    chat_id: int
    role: str
    content: str
    # date_created: str
    
class ChatResponse(BaseModel):
    id: int
    title: str
    project_id: int
    user_id: int
    
    messages: List[MessageResponse]
    
class ChatPostMessageRequest(BaseModel):
    chat_id: int
    content: str
