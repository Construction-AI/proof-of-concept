from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class QueryRequest(BaseModel):
    """Query request model"""
    text: str
    num_results: int = 3

class QueryResult(BaseModel):
    """Query result model"""
    node_id: str
    score: float
    text: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class QueryResponse(BaseModel):
    """Query response model"""
    results: List[QueryResult]
    query: str
    status: str = "success"
    timestamp: datetime = Field(default_factory=datetime.now)

class IndexingResult(BaseModel):
    """Result of indexing operation"""
    status: str
    message: str
    documents_processed: int = 0
    documents_failed: List[str] = Field(default_factory=list)
    index_info: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)