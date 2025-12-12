from abc import ABC
from pydantic import BaseModel
from typing import Optional

class KnowledgeBaseRequest(ABC):
    def __init__(self):
        pass
    
    class AddDocument(BaseModel):
        company_id: str
        project_id: str
        document_category: str
        document_type: str
        local_path: str
        
    class Query(BaseModel):
        question: str
        company_id: str
        project_id: str
        
        # Optional arguments to make request more specific
        document_type: Optional[str] = None
        document_category: Optional[str] = None
        file_name: Optional[str] = None
                
    class Delete(BaseModel):
        company_id: str
        project_id: str
        document_category: str
        document_type: str