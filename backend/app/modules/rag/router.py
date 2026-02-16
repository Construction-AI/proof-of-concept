from fastapi import APIRouter, Depends, status, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from typing import Any, List

from app.modules.rag.schemas import QueryDocsRequest, QueryResponse, QueryProjectRequest
from app.modules.rag.service import RagService

from app.db.session import get_db

from app.modules.auth.dependencies import get_current_user
from app.modules.auth import models as auth_models

router = APIRouter()

@router.post("/q/docs", response_model=QueryResponse)
async def query(
    query_in: QueryDocsRequest,
    db: Session = Depends(get_db),
    current_user: auth_models.User = Depends(get_current_user)
) -> Any:
    response: str = await RagService.query_documents(db=db, question=query_in.question, document_ids=query_in.document_ids, user_id=current_user.id)
    return QueryResponse(
        response=response
    )
    
@router.post("/q/project", response_model=QueryResponse)
async def query(
    query_in: QueryProjectRequest,
    db: Session = Depends(get_db),
    current_user: auth_models.User = Depends(get_current_user)
) -> Any:
    try:
        response: str = await RagService.query_project(db=db, question=query_in.question, project_id=query_in.project_id, user_id=current_user.id)
        return QueryResponse(
            response=response
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))