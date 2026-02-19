from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import Any

from app.modules.rag.schemas import QueryDocsRequest, QueryResponse, QueryProjectRequest, FinalResponse, DynamicRAGRequest, TYPE_MAP
from app.modules.rag.service import RagService

from app.db.session import get_db

from app.modules.auth.dependencies import get_current_user
from app.modules.auth import models as auth_models

router = APIRouter()

@router.post("/q/docs", response_model=QueryResponse)
async def query_docs(
    query_in: QueryDocsRequest,
    db: Session = Depends(get_db),
    current_user: auth_models.User = Depends(get_current_user)
) -> Any:
    try:
        response: str = await RagService.query_documents(db=db, question=query_in.question, document_ids=query_in.document_ids, user_id=current_user.id)
        return QueryResponse(
            response=response
        )
    except Exception as e:
        raise HTTPException(
            detail=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
@router.post("/q/project", response_model=QueryResponse)
async def query_project(
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
    
@router.post("/c/project", response_model=FinalResponse)
async def query_project_with_confidence(
    query_in: QueryProjectRequest,
    db: Session = Depends(get_db),
    current_user: auth_models.User = Depends(get_current_user)
) -> Any:
    try:
        response: dict[str, Any] = await RagService.query_with_confidence(db=db, question=query_in.question, project_id=query_in.project_id, user_id=current_user.id)
        return FinalResponse(
            structured_answer=response["answer"],
            sources=response["sources"]
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
@router.post("/q/dynamic")
async def ask_rag_dynamic(
    request: DynamicRAGRequest,
    db: Session = Depends(get_db),
    current_user: auth_models.User = Depends(get_current_user)
    ):
    target_python_type = TYPE_MAP[request.output_format]

    try:
        result = await RagService.query_with_dynamic_type(
            db=db,
            instruction=request.instruction,
            output_type=target_python_type,
            document_ids=request.document_ids,
            user_id=current_user.id
        )
        return result

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))