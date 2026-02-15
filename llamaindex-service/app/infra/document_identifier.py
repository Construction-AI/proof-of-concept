from fastapi import UploadFile
from typing import Optional
import uuid

class DocumentIdentifier:
    def __init__(self, project_id: int, user_id: int, document_name: Optional[str] = None, file: Optional[UploadFile] = None):
        assert(document_name or file, "Either `document_name` or `file` is required")
        
        self.project_id = str(project_id)
        self.user_id = str(user_id)
        self.document_name = document_name or f"{uuid.uuid4()}-{file.filename}"
        
    @staticmethod
    def from_storage_key(storage_key: str):
        segments = storage_key.split("/")
        identifier = DocumentIdentifier(
            project_id=segments[1],
            user_id=segments[2],
            document_name=segments[3]
        )
        return identifier
    
    @property
    def storage_key(self) -> str:
        return f"projects/{self.user_id}/{self.project_id}/{self.document_name}"
    
        