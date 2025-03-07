from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class DocumentMetadata(BaseModel):
    """Metadata for a document"""
    filename: str
    file_path: str
    file_size: int
    created_at: datetime = Field(default_factory=datetime.now)
    mime_type: Optional[str] = None
    page_count: Optional[int] = None
    additional_info: Dict[str, Any] = Field(default_factory=dict)

class Document(BaseModel):
    """Document model"""
    id: Optional[str] = None
    content: str
    metadata: DocumentMetadata

class DocumentGenerationRequest(BaseModel):
    """Request model for document generation"""
    project_name: str
    industry: str
    document_type: str

class GeneratedDocument(BaseModel):
    """Generated document response"""
    content: str
    document_type: str
    generated_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)