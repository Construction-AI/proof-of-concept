from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request, Depends, Path
from typing import List, Dict, Any
import os
import logging

from app.services.indexing_service import IndexingService
from app.services.document_generator import DocumentGeneratorService

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["api"])

# Initialize the indexing service with the correct path
def get_indexing_service(request: Request):
    documents_dir = request.app.state.documents_dir
    return IndexingService(documents_dir=documents_dir)

def get_document_generator(indexing_service: IndexingService = Depends(get_indexing_service)):
    """Get DocumentGeneratorService instance"""
    return DocumentGeneratorService(indexing_service)

@router.post("/process")
async def process_directory(
    indexing_service: IndexingService = Depends(get_indexing_service)
):
    """Process all documents in the specified directory"""
    result = indexing_service.process_directory()
    
    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result["message"])
        
    return result

@router.post("/query")
async def query_index(
    query: Dict[str, Any],
    indexing_service: IndexingService = Depends(get_indexing_service)
):
    """Query the index with the given text"""
    query_text = query.get("text", "")
    num_results = query.get("num_results", 3)
    
    if not query_text:
        raise HTTPException(status_code=400, detail="Query text is required")
        
    result = indexing_service.query_index(query_text, num_results)
    
    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result["message"])
        
    return result

@router.delete("/clear")
async def clear_documents(
    indexing_service: IndexingService = Depends(get_indexing_service)
):
    """Clear the documents collection"""
    result = indexing_service.clear_documents()
    
    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result["message"])
        
    return result

@router.get("/health")
async def health_check():
    return {"status": "healthy"}

@router.post("/generate-document")
async def generate_document(
    request: Request,
    project_name: str = Form(...),
    industry: str = Form(...),
    document_type: str = Form(...),
    indexing_service: IndexingService = Depends(get_indexing_service),
    document_generator: DocumentGeneratorService = Depends(get_document_generator)
):
    """
    Process existing documents in the documents directory and generate a document
    
    Args:
        project_name: Name of the project
        industry: Industry of the project
        document_type: Type of document to generate
        
    Returns:
        Document generation result (raw JSON)
    """
    try:
        # Get documents directory from app state
        documents_dir = request.app.state.documents_dir
        
        # Check if directory has files
        files_in_directory = [f for f in os.listdir(documents_dir) if os.path.isfile(os.path.join(documents_dir, f))]
        
        if not files_in_directory:
            raise HTTPException(status_code=400, detail="No files found in documents directory")
        
        # Log the files found
        logger.info(f"Found {len(files_in_directory)} files in documents directory: {files_in_directory}")
        
        # Process and index the documents
        logger.info(f"Indexing documents for project: {project_name}")
        indexing_result = indexing_service.process_directory()
        
        if indexing_result.get("status") == "error":
            raise HTTPException(status_code=400, detail=indexing_result.get("message", "Error during indexing"))
        
        # Generate document content
        logger.info(f"Generating {document_type} for project: {project_name}")
        generation_result = document_generator.generate_document(
            project_name=project_name,
            industry=industry,
            document_type=document_type
        )
        
        # Return the raw result
        return generation_result
        
    except Exception as e:
        logger.error(f"Error processing documents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing documents: {str(e)}")