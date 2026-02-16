from sqlalchemy.orm import Session, joinedload
from app.modules.projects import models, schemas

class ProjectService:
    
    @staticmethod
    def create_project(db: Session, project: schemas.ProjectCreate, user_id: int):
        db_project = models.Project(
            title=project.title,
            description=project.description,
            owner_id=user_id,
        )
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        return db_project
    
    @staticmethod
    def get_project_by_id(db: Session, project_id: int):
        return (
            db.query(models.Project)
            .filter(models.Project.id == project_id)
            .first()
        )
        
    @staticmethod
    def get_projects_by_ids(db: Session, project_ids: list[int]):
        projects = []
        for id in project_ids:
            projects.append(ProjectService.get_project_by_id(db=db, project_id=id))
        return projects
        
    @staticmethod
    def get_projects_by_owner(db: Session, owner_id: int):
        return db.query(models.Project).filter(models.Project.owner_id == owner_id).all()
    
    @staticmethod
    def get_all_projects(db: Session):
        return (
            db.query(models.Project)
            .options(joinedload(models.Project.owner))
            .all()
        )