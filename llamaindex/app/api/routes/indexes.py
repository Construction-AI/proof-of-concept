from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any

from app.services.indexing_service import IndexingService
from app.api.dependencies import get_indexing_service

router = APIRouter(prefix="/indexes", tags=["indexes"])

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
    """
    Query the index with the given text
    
    Args:
        query: Query object with text and options
            - text: Query text
            - num_results: Number of results to return (default: 3)
            
    Returns:
        Query results
    """
    query_text = query.get("text", "")
    num_results = query.get("num_results", 3)
    
    if not query_text:
        raise HTTPException(status_code=400, detail="Query text is required")
        
    result = indexing_service.query_index(query_text, num_results)
    
    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result["message"])
        
    return result