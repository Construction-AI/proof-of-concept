from sqlalchemy.orm import Session, joinedload
from fastapi import UploadFile

from app.core.logger import get_logger
from app.infra.storage import storage_client
from app.infra.document_identifier import DocumentIdentifier
from app.infra.vector_store import vector_store_client

from app.modules.documents.models import Document
from app.modules.documents.schemas import DocumentCreate

from app.modules.projects.models import Project
from app.modules.projects.service import ProjectService
from app.modules.projects.security import project_check_user_access


class DocumentService:
    LOGGER = get_logger("DocumentService")
    
    @staticmethod
    async def create_document(db: Session, file: UploadFile, document: DocumentCreate, user_id: int):
        project: Project = ProjectService.get_project_by_id(db=db, project_id=document.project_id)
        project_check_user_access(user_id=user_id, project=project)
        identifier: DocumentIdentifier = DocumentIdentifier(
            project_id=document.project_id,
            user_id=user_id,
            file=file
        )
        
        file_uploaded = False
        file_indexed = False
        
        try:
            # 1. Storage Upload
            storage_client.upload_file(file_obj=file, object_name=identifier.storage_key,
                                    content_type=file.content_type)
            file_uploaded = True
            file.file.seek(0)
            
            # 2. Indexing
            await vector_store_client.upload_document(file=file, identifier=identifier)
            file_indexed = True
            file.file.seek(0)
        
            # 3. DB Insert
            db_document = Document(
                file_name=file.filename,
                storage_key=identifier.storage_key,
                content_type=file.content_type,
                size=file.size,
                owner_id=user_id,
                project_id=document.project_id,
                content_hash=DocumentService.get_document_content_hash(file=file)
            )
            
            db.add(db_document)
            db.commit()
            db.refresh(db_document)
            return db_document
        except Exception as e:
            db.rollback()
        
            if file_uploaded:
                try:
                    DocumentService.LOGGER.warning(f"Rolling back file upload: {identifier.storage_key}")
                    storage_client.delete_file(object_name=identifier.storage_key)
                except Exception as delete_error:
                    DocumentService.LOGGER.error(f"Failed to rollback file {identifier.storage_key}: {str(delete_error)}")        
            if file_indexed:
                try:
                    DocumentService.LOGGER.warning(f"Rolling back file indexing: {identifier.storage_key}")
                    await vector_store_client.delete_document(identifier=identifier)
                except Exception as delete_error:
                    DocumentService.LOGGER.error(f"Failed to rollback index {identifier.storage_key}: {str(delete_error)}")
            raise e
        
    @staticmethod
    async def delete_document(db: Session, document_id: int, user_id: int):
        document: Document = DocumentService.get_document_by_id(db=db, document_id=document_id)
        if not document or document.owner_id != user_id:
            raise Exception("Document not found or belongs to another user.")
        identifier: DocumentIdentifier = DocumentIdentifier.from_storage_key(storage_key=document.storage_key)
        try:
            # 0. DB
            db.delete(document)
            db.commit()
            
            # 1. File storage
            storage_client.delete_file(object_name=identifier.storage_key)
            # TODO: Add rollback
            
            # 2. Qdrant
            await vector_store_client.delete_document(identifier=identifier)
            # TODO: Add rollback
            
            return None
        except Exception as e:
            db.rollback()
            DocumentService.LOGGER.error(f"[Delete Document] Failed to delete document: {str(e)}")
            
            # TODO: Add rollbacks
            raise e
    
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
        return storage_client.get_download_url(storage_key=document.storage_key)
    
    @staticmethod
    def get_documents_by_ids(db: Session, document_ids: list[int]):
        docs: list[Document] = []
        for id in document_ids:
            doc: Document = DocumentService.get_document_by_id(db=db, document_id=id)
            docs.append(doc)
        return docs
        
    @staticmethod
    def get_documents_by_project_id(db: Session, project_id: int, user_id: int):
        project: Project = ProjectService.get_project_by_id(db=db, project_id=project_id)
        if not project or project.owner_id != user_id:
            raise Exception("Project does not exist or belongs to another user")
        return db.query(Document).filter(Document.project_id == project_id).all()
            
    
    @staticmethod
    async def query_document(db: Session, question: str, document_id: int, user_id: int):
        document: Document = DocumentService.get_document_by_id(db=db, document_id=document_id)
        if not document:
            raise Exception(f"[Query Document] Document `{document_id}` was not found.")
        if not document.owner_id == user_id:
            raise Exception(f"[Query Document] Document `{document_id}` does not belong to current user.")
        return await vector_store_client.query(question=question, storage_keys=[document.storage_key])
    
    @staticmethod
    def get_document_content_hash(file: UploadFile) -> str:
        import hashlib
        hasher = hashlib.sha256()
        CHUNK_SIZE = 8192
        file.file.seek(0)
        
        for chunk in iter(lambda: file.file.read(CHUNK_SIZE), b""):
            hasher.update(chunk)
        
        file.file.seek(0)
        return hasher.hexdigest()
