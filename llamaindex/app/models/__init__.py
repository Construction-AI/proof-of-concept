# Re-export models for easier imports
from app.models.document import (
    Document, 
    DocumentMetadata, 
    DocumentGenerationRequest,
    GeneratedDocument
)

from app.models.index import (
    QueryRequest,
    QueryResult,
    QueryResponse,
    IndexingResult
)