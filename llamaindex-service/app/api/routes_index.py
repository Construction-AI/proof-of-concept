from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
from app.services.index_service import build_project_index, get_existing_project_indexes, load_project_indices

router = APIRouter()

class IndexRequest(BaseModel):
    directory_path: str
    project_id: str

class StatusResponse(BaseModel):
    status: str
    message: str


@router.post("", response_model=StatusResponse)
async def create_index(request: IndexRequest):
    doc_path = Path(request.directory_path)
    if not doc_path.exists():
        raise HTTPException(status_code=400, detail=f"Directory not found: {request.directory_path}")
    try:
        build_project_index(request.directory_path, request.project_id)
        return StatusResponse(
            status="Success",
            message=f"Indexed project '{request.project_id}'"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/all", response_model=list)
async def get_all_indexes():
    try:
        indexes = await get_existing_project_indexes()
        return indexes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/preload", response_model=StatusResponse)
async def preload_indices():
    try:
        await load_project_indices()
        return StatusResponse(
            status="Success",
            message="Indices preloaded"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))