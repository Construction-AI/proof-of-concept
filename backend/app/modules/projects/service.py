from sqlalchemy.orm import Session, joinedload
from fastapi import Depends

from app.core.logger import get_logger
from app.db.session import get_db
from app.modules.projects import models, schemas
from app.modules.projects.models import Project

class ProjectService:
    def __init__(self, db: Session):
        self.db = db
        self.logger = get_logger(self.__class__.__name__)
    
    def create_project(self, project: schemas.ProjectCreate, user_id: int):
        db_project = models.Project(
            title=project.title,
            description=project.description,
            owner_id=user_id,
        )
        self.db.add(db_project)
        self.db.commit()
        self.db.refresh(db_project)
        return db_project
    
    def get_project_by_id(self, project_id: int):
        return (
            self.db.query(models.Project)
            .filter(models.Project.id == project_id)
            .first()
        )
        
    def get_projects_by_ids(self, project_ids: list[int]) -> list[Project]:
        projects: list[Project] = []
        for id in project_ids:
            projects.append(self.get_project_by_id(project_id=id))
        return projects
        
    def get_projects_by_owner(self, owner_id: int):
        return self.db.query(models.Project).filter(models.Project.owner_id == owner_id).all()
    
    def get_all_projects(self, db: Session):
        return (
            self.db.query(models.Project)
            .options(joinedload(models.Project.owner))
            .all()
        )
        
    def get_storage_keys_for_project_id(self, user_id: int, project_id: int):
        from app.modules.documents.models import Document
        from app.modules.documents.service import DocumentService
        
        project: Project = self.get_project_by_id(project_id=project_id)
        if not project or project.owner_id != user_id:
            raise Exception(f"Project `{project_id}` does not exist or belongs to different user.")

        document_service = DocumentService(db=self.db)
        docs: list[Document] = document_service.get_documents_by_project_id(project_id=project_id, user_id=user_id)
        storage_keys: list[str] = [doc.storage_key for doc in docs]
        return storage_keys
    
def get_project_service(db: Session = Depends(get_db)):
    return ProjectService(db=db)