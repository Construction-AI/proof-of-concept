from pydantic import BaseModel
from abc import ABC

class FileStorageRequest(ABC):
    class Upload(BaseModel):
        local_file_path: str
        company_id: str
        project_id: str
        document_category: str

    class Upsert(BaseModel):
        local_file_path: str
        company_id: str
        project_id: str
        document_category: str

    class Delete(BaseModel):
        company_id: str
        project_id: str
        document_category: str
