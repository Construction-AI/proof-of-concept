from fastapi import Depends
from sqlalchemy.orm import Session

from app.modules.documents.service import DocumentService
from app.db.session import get_db

def get_document_service(db: Session = Depends(get_db)) -> DocumentService:
    return DocumentService(db=db)