from fastapi import Request, Depends
from app.services.indexing_service import IndexingService
from app.services.document_generator import DocumentGeneratorService

def get_indexing_service(request: Request) -> IndexingService:
    """
    Get the IndexingService instance with the documents directory from the app state
    
    Args:
        request: FastAPI request object
    
    Returns:
        IndexingService: Configured indexing service
    """
    documents_dir = request.app.state.documents_dir
    return IndexingService(documents_dir=documents_dir)

def get_document_generator(
    indexing_service: IndexingService = Depends(get_indexing_service)
) -> DocumentGeneratorService:
    """
    Get DocumentGeneratorService instance
    
    Args:
        indexing_service: Injected IndexingService instance
    
    Returns:
        DocumentGeneratorService: Configured document generator service
    """
    return DocumentGeneratorService(indexing_service)