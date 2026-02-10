from sqlalchemy.orm import Session, joinedload
from app.modules.documents import models, schemas

class DocumentService:
    
    @staticmethod
    def create_document(db: Session, document: schemas.DocumentCreate, user_id: int):
        db_document = models.Document(
            title=document.title,
            description=document.description,
            file_url=document.file_url,
            owner_id=user_id,
            project_id=document.project_id
        )
        
        db.add(db_document)
        # TODO: Verify whether project of given ID exists
        # TODO: Add file upload and indexing logic here
        db.commit()
        db.refresh(db_document)
        return db_document
    
    # TODO: Add checks on whether the user has access to the document or not
    @staticmethod
    def get_document_by_id(db: Session, document_id: int):
        return (
            db.query(models.Document)
            .filter(models.Document.id == document_id)
            .first()
        )
        
    @staticmethod
    def get_documents_by_owner(db: Session, owner_id: int):
        return db.query(models.Document).filter(models.Document.owner_id == owner_id).all()
    
    @staticmethod
    def get_all_documents(db: Session):
        return (
            db.query(models.Document)
            .options(joinedload(models.Document.owner))
            .all()
        )