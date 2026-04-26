from fastapi import APIRouter, Depends, status, HTTPException
from typing import Any

from app.core.logger import get_logger
from app.modules.auth.dependencies import get_current_user
from app.modules.auth import models as auth_models

import app.modules.rag.service as rag_service
import app.modules.rag.schemas as rag_schemas

router = APIRouter()

@router.post("/q/docs", response_model=rag_schemas.QueryResponse)
async def query_docs(
    query_in: rag_schemas.QueryDocsRequest,
    rag_service: rag_service.RagService = Depends(rag_service.get_rag_service),
    current_user: auth_models.User = Depends(get_current_user)
) -> Any:
    try:
        response: str = await rag_service.query_documents(question=query_in.question, document_ids=query_in.document_ids, user_id=current_user.id)
        return rag_schemas.QueryResponse(
            response=response
        )
    except Exception as e:
        raise HTTPException(
            detail=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
@router.post("/q/project", response_model=rag_schemas.QueryResponse)
async def query_project(
    query_in: rag_schemas.QueryProjectRequest,
    rag_service: rag_service.RagService = Depends(rag_service.get_rag_service),
    current_user: auth_models.User = Depends(get_current_user)
) -> Any:
    try:
        response: str = await rag_service.query_project(question=query_in.question, project_id=query_in.project_id, user_id=current_user.id)
        return rag_schemas.QueryResponse(
            response=response
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
@router.post("/c/project", response_model=rag_schemas.FinalResponse)
async def query_project_with_confidence(
    query_in: rag_schemas.QueryProjectRequest,
    rag_service: rag_service.RagService = Depends(rag_service.get_rag_service),
    current_user: auth_models.User = Depends(get_current_user)
) -> Any:
    try:
        response: dict[str, Any] = await rag_service.query_with_confidence(question=query_in.question, project_id=query_in.project_id, user_id=current_user.id)
        return rag_schemas.FinalResponse(
            structured_answer=response["answer"],
            sources=response["sources"]
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
@router.post("/q/dynamic")
async def ask_rag_dynamic(
    request: rag_schemas.DynamicRAGRequest,
    rag_service: rag_service.RagService = Depends(rag_service.get_rag_service),
    current_user: auth_models.User = Depends(get_current_user)
    ):
    logger = get_logger(ask_rag_dynamic.__name__)
    target_python_type = rag_schemas.TYPE_MAP[request.output_format]
    try:
        logger.info(f"Received RAG query with dynamic type from user: {current_user.id}, instruction: {request.instruction}")
        result = await rag_service.query_with_dynamic_type(
            instruction=request.instruction,
            output_type=target_python_type,
            project_id=request.project_id,
            user_id=current_user.id
        )
        return rag_schemas.DynamicRAGResponse(**result)
    except Exception as e:
        logger.error(f"Failed to complete RAG query with dynamic type: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))