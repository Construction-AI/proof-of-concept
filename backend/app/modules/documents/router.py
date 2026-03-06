from fastapi import APIRouter, Depends, status, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from typing import Any, List

from app.db.session import get_db

from app.modules.documents import schemas as document_schemas
from app.modules.documents.service import DocumentService

from app.modules.auth.dependencies import get_current_user
from app.modules.auth import models as auth_models

router = APIRouter()

@router.post("/create", response_model=document_schemas.DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
    project_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: auth_models.User = Depends(get_current_user)
) -> Any:
    try:
        document_in = document_schemas.DocumentCreate(project_id=project_id)
        new_document = await DocumentService.create_document(db=db, file=file, document=document_in, user_id=current_user.id)
        return new_document
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/download_url/{document_id}")
def get_download_url_for_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: auth_models.User = Depends(get_current_user),
) -> Any:
    return DocumentService.get_document_download_url(db=db, document_id=document_id, user_id=current_user.id)

@router.get("/", response_model=List[document_schemas.DocumentResponse])
def read_my_documents(
    db: Session = Depends(get_db),
    current_user: auth_models.User = Depends(get_current_user)
) -> Any:
    return DocumentService.get_documents_by_owner(db=db, owner_id=current_user.id)

@router.delete("/{document_id}")
async def delete(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: auth_models.User = Depends(get_current_user)
) -> Any:
    return await DocumentService.delete_document(db=db, document_id=document_id, user_id=current_user.id)

@router.get("/{document_id}/validate")
async def validate(
    document_id: int,
    db: Session = Depends(get_db)
    # TODO: Maybe add current user
) -> Any:
    return await DocumentService.validate_document_sync(db=db, document_id=document_id)
    