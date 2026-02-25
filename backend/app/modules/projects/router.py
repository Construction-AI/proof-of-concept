from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import Any, List

from app.db.session import get_db

from app.modules.projects import schemas as project_schemas
from app.modules.projects import service as project_service

from app.modules.auth.dependencies import get_current_user
from app.modules.auth import models as auth_models

router = APIRouter()

@router.post("/create", response_model=project_schemas.ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project_in: project_schemas.ProjectCreate,
    db: Session = Depends(get_db),
    current_user: auth_models.User = Depends(get_current_user)
) -> Any:
    new_project = project_service.ProjectService.create_project(db=db, project=project_in, user_id=current_user.id)
    return new_project

@router.get("", response_model=List[project_schemas.ProjectResponse])
def read_my_projects(
    db: Session = Depends(get_db),
    current_user: auth_models.User = Depends(get_current_user)
) -> Any:
    return project_service.ProjectService.get_projects_by_owner(db=db, owner_id=current_user.id)