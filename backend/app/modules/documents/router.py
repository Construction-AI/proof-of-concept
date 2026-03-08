from fastapi import APIRouter, Depends, status, UploadFile, File, Form, HTTPException
from typing import Any, List

from app.modules.documents import schemas as document_schemas
from app.modules.documents.service import DocumentService
from app.modules.documents.dependencies import get_document_service

from app.modules.auth.dependencies import get_current_user
from app.modules.auth import models as auth_models

router = APIRouter()

@router.post("/create", response_model=document_schemas.DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
    project_id: int = Form(...),
    file: UploadFile = File(...),
    current_user: auth_models.User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service)
) -> Any:
    try:
        new_document = await document_service.create_document(file=file, project_id=project_id, user_id=current_user.id)
        return new_document
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/download_url/{document_id}")
def get_download_url_for_document(
    document_id: int,
    current_user: auth_models.User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service)
) -> Any:
    return document_service.get_document_download_url(document_id=document_id, user_id=current_user.id)

@router.get("/", response_model=List[document_schemas.DocumentResponse])
def read_my_documents(
    current_user: auth_models.User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service)
) -> Any:
    return document_service.get_documents_by_owner(owner_id=current_user.id)

@router.delete("/{document_id}")
async def delete(
    document_id: int,
    current_user: auth_models.User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service)
) -> Any:
    return await document_service.delete_document(document_id=document_id, user_id=current_user.id)

@router.get("/{document_id}/validate")
async def validate(
    document_id: int,
    document_service: DocumentService = Depends(get_document_service)
    # TODO: Maybe add current user
) -> Any:
    doc_status: dict[str, bool] = await document_service.validate_document_sync(document_id=document_id)
    return document_schemas.DocumentValidationResponse(**doc_status)

@router.post("/{document_id}/reupload")
async def reupload(
    document_id: int,
    file: UploadFile = File(...),
    current_user: auth_models.User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service)   
) -> Any:
    return await document_service.reupload_document(file=file, document_id=document_id, user_id=current_user.id)