from fastapi import APIRouter, Form, HTTPException, Request, Depends
import os
import logging

from app.api.dependencies import get_indexing_service, get_document_generator
from app.services.indexing_service import IndexingService
from app.services.document_generator import DocumentGeneratorService

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/generate")
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
        
        # Skip re-indexing since documents are processed on upload
        # Generate document content directly
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

@router.delete("/clear")
async def clear_documents(
    indexing_service: IndexingService = Depends(get_indexing_service)
):
    """Clear the documents collection"""
    result = indexing_service.clear_documents()
    
    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result["message"])
        
    return result