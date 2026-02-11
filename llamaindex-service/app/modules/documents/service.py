from sqlalchemy.orm import Session, joinedload
from fastapi import UploadFile
import uuid
from app.infra.storage import storage_client

from app.modules.documents.models import Document
from app.modules.documents.schemas import DocumentCreate

from app.modules.projects.models import Project
from app.modules.projects.service import ProjectService


class DocumentService:
    
    @staticmethod
    def create_document(db: Session, file: UploadFile, document: DocumentCreate, user_id: int):
        # TODO: Check project ownership
        project: Project = ProjectService.get_project_by_id(db=db, project_id=document.project_id)
        if not project or project.owner_id != user_id:
            raise Exception("Project does not exist or belongs to another user")
        
        unique_file_name = f"{uuid.uuid4()}-{file.filename}"
        storage_key = f"projects/{document.project_id}/{unique_file_name}"
        
        storage_client.upload_file(file_obj=file, object_name=storage_key,
                                   content_type=file.content_type, project_id=document.project_id)
        
        # TODO: Add a rollback if anything happens after file upload
        db_document = Document(
            file_name=file.filename,
            file_storage_key=storage_key,
            content_type=file.content_type,
            size=file.size,
            owner_id=user_id,
            project_id=document.project_id,
        )
        
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        return db_document
    
    # TODO: Add checks on whether the user has access to the document or not
    @staticmethod
    def get_document_by_id(db: Session, document_id: int):
        return (
            db.query(Document)
            .filter(Document.id == document_id)
            .first()
        )
        
    @staticmethod
    def get_documents_by_owner(db: Session, owner_id: int):
        return db.query(Document).filter(Document.owner_id == owner_id).all()
    
    @staticmethod
    def get_all_documents(db: Session):
        return (
            db.query(Document)
            .options(joinedload(Document.owner))
            .all()
        )
        
    @staticmethod
    def get_document_download_url(db: Session, document_id: int, user_id: int):
        document: Document = DocumentService.get_document_by_id(db=db, document_id=document_id)
        if not document or document.owner_id != user_id:
            raise Exception("Document does not exist or belongs to another user")
        return storage_client.get_download_url(storage_key=document.file_storage_key)