from fastapi import APIRouter, HTTPException, Path, Depends
from typing import Dict, Any

from app.services.indexing_service import IndexingService
from fastapi import Request

router = APIRouter(prefix="/api", tags=["api"])

# Initialize the indexing service with the correct path
def get_indexing_service(request: Request):
	documents_dir = request.app.state.documents_dir
	return IndexingService(documents_dir=documents_dir)

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