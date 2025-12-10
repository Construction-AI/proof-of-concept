from abc import ABC
from pydantic import BaseModel

class KnowledgeBaseRequest(ABC):
    def __init__(self):
        pass
    
    class AddDocument(BaseModel):
        company_id: str
        project_id: str
        document_category: str
        document_type: str
        local_path: str