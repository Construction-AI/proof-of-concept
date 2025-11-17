from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.rag_engine import query_project

router = APIRouter()

class QueryResponse(BaseModel):
    message: str

class QueryRequest(BaseModel):
    question: str
    project_id: str

@router.get("", response_model=QueryResponse)
def query(req: QueryRequest):
    try:
        res = query_project(project_id=req.project_id, question=req.question)
        return QueryResponse(
            message=res.response
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
