from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.api.services.document_loader import build_project_index as bpi

router = APIRouter()

class IndexRequest(BaseModel):
    project_id: str
    directory_path: str

class IndexResponse(BaseModel):
    status: str 
    message: str

@router.post("", response_model=IndexResponse)
async def build_project_index(req: IndexRequest):
    try:
        await bpi(req.directory_path, req.project_id)
        return IndexResponse(
            status="Success",
            message=f"Directory {req.directory_path} has been indexed as project {req.project_id}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
