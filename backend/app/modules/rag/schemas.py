from pydantic import BaseModel
from typing import List

class QueryDocsRequest(BaseModel):
    question: str
    document_ids: List[int]
    
class QueryProjectRequest(BaseModel):
    question: str
    project_id: int

class QueryResponse(BaseModel):
    response: str