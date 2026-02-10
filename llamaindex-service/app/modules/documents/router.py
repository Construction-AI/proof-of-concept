from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import Any, List

from app.db.session import get_db

from app.modules.documents import schemas as document_schemas
from app.modules.documents import service as document_service

from app.modules.auth.dependencies import get_current_user
from app.modules.auth import models as auth_models

router = APIRouter()

@router.post("/create", response_model=document_schemas.DocumentResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    document_in: document_schemas.DocumentCreate,
    db: Session = Depends(get_db),
    current_user: auth_models.User = Depends(get_current_user)
) -> Any:
    new_document = document_service.DocumentService.create_document(db=db, document=document_in, user_id=current_user.id)
    return new_document
    
@router.get("/", response_model=List[document_schemas.DocumentResponse])
def read_my_documents(
    db: Session = Depends(get_db),
    current_user: auth_models.User = Depends(get_current_user)
) -> Any:
    return document_service.DocumentService.get_documents_by_owner(db=db, owner_id=current_user.id)