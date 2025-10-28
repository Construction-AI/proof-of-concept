from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.query_service import query_documents

router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    project_id: str

@router.post("")
async def query_endpoint(req: QueryRequest):
    try:
        return query_documents(req.project_id, req.query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))