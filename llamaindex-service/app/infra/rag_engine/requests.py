from pydantic import BaseModel
from typing import Optional

class RagEngineRequest:
    class UploadDocument(BaseModel):
        local_file_path: str
        company_id: str
        project_id: str
        document_category: str

    class UpsertDocument(BaseModel):
        local_file_path: str
        company_id: str
        project_id: str
        document_category: str

    class DeleteDocument(BaseModel):
        company_id: str
        project_id: str
        document_category: str
        
    class ReadDocument(BaseModel):
        company_id: str
        project_id: str
        document_category: str
        document_type: str
        
        # Optional: specify if more than one file
        file_name: Optional[str] = None
        
    class QueryKnowledgeBase(BaseModel):
        question: str
        company_id: str
        project_id: str
        
        # Optional arguments to make request more specific
        document_type: Optional[str] = None
        document_category: Optional[str] = None
        file_name: Optional[str] = None
        
    class GenerateSchema(BaseModel):
        company_id: str
        project_id: str
        document_category: str
        
    class GenerateDocument(BaseModel):
        company_id: str
        project_id: str
        document_category: str
        author: str
        
    class GenerateDocx(BaseModel):
        company_id: str
        project_id: str
        document_category: str
        
    