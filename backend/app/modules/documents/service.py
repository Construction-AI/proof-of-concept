from sqlalchemy.orm import Session, joinedload
from fastapi import UploadFile, HTTPException, status, Depends

from app.db.session import get_db
from app.core.logger import get_logger
from app.infra.storage import storage_client
from app.infra.document_identifier import DocumentIdentifier
from app.infra.vector_store import vector_store_client

from app.modules.documents.models import Document

class DocumentService:
    def __init__(self, db: Session):
        self.db = db
        self.logger = get_logger(self.__class__.__name__)        
        
    async def create_document(self, file: UploadFile, project_id: int, user_id: int):
        identifier = DocumentIdentifier(
            project_id=project_id,
            user_id=user_id,
            file=file
        )
        
        file_uploaded = False
        file_indexed = False
        
        try:
            # 1. Storage Upload
            file_uploaded = self._upload_document_to_fs(file=file, document_identifier=identifier)
            
            # 2. Indexing
            file_indexed = await self._upload_document_to_vs(file=file, document_identifier=identifier)
        
            # 3. DB Insert
            db_document = Document(
                file_name=file.filename,
                storage_key=identifier.storage_key,
                content_type=file.content_type,
                size=file.size, 
                owner_id=user_id,
                project_id=project_id,
                content_hash=self.get_document_content_hash(file=file)
            )
            
            self.db.add(db_document)
            self.db.commit()
            self.db.refresh(db_document)
            return db_document
        except Exception as e:
            self.db.rollback()
        
            if file_uploaded:
                try:
                    self.logger.warning(f"Rolling back file upload: {identifier.storage_key}")
                    storage_client.delete_file(object_name=identifier.storage_key)
                except Exception as delete_error:
                    self.logger.error(f"Failed to rollback file {identifier.storage_key}: {str(delete_error)}")        
            if file_indexed:
                try:
                    self.logger.warning(f"Rolling back file indexing: {identifier.storage_key}")
                    await vector_store_client.delete_document(identifier=identifier)
                except Exception as delete_error:
                    self.logger.error(f"Failed to rollback index {identifier.storage_key}: {str(delete_error)}")
            raise e

        
    async def delete_document(self, document_id: int, user_id: int):
        document: Document = self.get_document_by_id(document_id=document_id)
        if not document or document.owner_id != user_id:
            raise Exception("Document not found or belongs to another user.")
        identifier: DocumentIdentifier = DocumentIdentifier.from_storage_key(storage_key=document.storage_key)
        try:
            # 0. DB
            self.db.delete(document)
            self.db.commit()
            
            # 1. File storage
            storage_client.delete_file(object_name=identifier.storage_key)
            # TODO: Add rollback
            
            # 2. Qdrant
            await vector_store_client.delete_document(identifier=identifier)
            # TODO: Add rollback
            
            return None
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Failed to delete document: {str(e)}")
            
            # TODO: Add rollbacks
            raise e
    
    # TODO: Add checks on whether the user has access to the document or not
    def get_document_by_id(self, document_id: int) -> Document | None:
        return (
            self.db.query(Document)
            .filter(Document.id == document_id)
            .first()
        )
        
    def get_documents_by_owner(self, owner_id: int):
        return self.db.query(Document).filter(Document.owner_id == owner_id).all()
    
    def get_all_documents(self):
        return (
            self.db.query(Document)
            .options(joinedload(Document.owner))
            .all()
        )
        
    def get_document_download_url(self, document_id: int, user_id: int):
        document: Document = self.get_document_by_id(document_id=document_id)
        if not document or document.owner_id != user_id:
            raise Exception("Document does not exist or belongs to another user")
        return storage_client.get_download_url(storage_key=document.storage_key)
    
    def get_documents_by_ids(self, document_ids: list[int]):
        docs: list[Document] = []
        for id in document_ids:
            doc: Document = self.get_document_by_id(document_id=id)
            docs.append(doc)
        return docs
        
    def get_documents_by_project_id(self, project_id: int, user_id: int):
        # project: Project = ProjectService.get_project_by_id(project_id=project_id)
        # if not project or project.owner_id != user_id:
        #     raise Exception("Project does not exist or belongs to another user")
        
        # TODO: Perform ownership check on the project
        return self.db.query(Document).filter(Document.project_id == project_id).all()
            
    
    async def query_document(self, question: str, document_id: int, user_id: int):
        document: Document = self.get_document_by_id(document_id=document_id)
        if not document:
            raise Exception(f"[Query Document] Document `{document_id}` was not found.")
        if not document.owner_id == user_id:
            raise Exception(f"[Query Document] Document `{document_id}` does not belong to current user.")
        return await vector_store_client.query(question=question, storage_keys=[document.storage_key])
    
    def get_document_content_hash(self, file: UploadFile) -> str:
        import hashlib
        hasher = hashlib.sha256()
        CHUNK_SIZE = 8192
        file.file.seek(0)
        
        for chunk in iter(lambda: file.file.read(CHUNK_SIZE), b""):
            hasher.update(chunk)
        
        file.file.seek(0)
        return hasher.hexdigest()
    
    async def validate_document_sync(self, document_id: int) -> dict[str, bool]:
        response = {
            "db": False,
            "vector_store": False,
            "file_storage": False
        }
        
        doc: Document = self.get_document_by_id(document_id=document_id)
        if not doc:
            return response
        
        response["db"] = True
        exists_in_vector_store = await vector_store_client.check_document_exists(storage_key=doc.storage_key)
        exists_in_file_storage = storage_client.check_file_exists(storage_key=doc.storage_key)
        
        response["vector_store"] = exists_in_vector_store
        response["file_storage"] = exists_in_file_storage
        
        return response
    
    async def reupload_document(self, file: UploadFile, document_id: int, user_id: int):
        doc = self.get_document_by_id(document_id=document_id)
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Failed to delete requested file, missing from DB."
            )
        await self.delete_document(document_id=document_id, user_id=user_id)
        await self.create_document(file=file, project_id=doc.project_id, user_id=user_id)
        
        
    def _upload_document_to_fs(self, file: UploadFile, document_identifier: DocumentIdentifier) -> bool:
        storage_client.upload_file(file_obj=file, object_name=document_identifier.storage_key,
                                    content_type=file.content_type)
        file.file.seek(0)
        return True
    
    async def _upload_document_to_vs(self, file: UploadFile, document_identifier: DocumentIdentifier) -> bool:
        await vector_store_client.upload_document(file=file, identifier=document_identifier)
        file.file.seek(0)
        return True
        
def get_document_service(db: Session = Depends(get_db)) -> DocumentService:
    return DocumentService(db=db)