from fastapi import APIRouter, Depends, status
from typing import Any, List

from app.modules.auth.dependencies import get_current_user
from app.modules.auth import models as auth_models
from app.modules.projects.service import ProjectService, get_project_service
from app.modules.projects.schemas import ProjectCreate, ProjectResponse

router = APIRouter()

@router.post("/create", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project_in: ProjectCreate,
    project_service: ProjectService = Depends(get_project_service),
    current_user: auth_models.User = Depends(get_current_user)
) -> Any:
    new_project = project_service.create_project(project=project_in, user_id=current_user.id)
    return new_project

@router.get("", response_model=List[ProjectResponse])
def read_my_projects(
    project_service: ProjectService = Depends(get_project_service),
    current_user: auth_models.User = Depends(get_current_user)
) -> Any:
    return project_service.get_projects_by_owner(owner_id=current_user.id)

from typing import List
from app.modules.chats.schemas import ChatResponse, ChatCreateRequest
from app.modules.chats.service import ChatService, get_chat_service

@router.post("/{project_id}/chats", response_model=ChatResponse)
def create_project_chat(
    project_id: int,
    request: ChatCreateRequest,
    current_user: auth_models.User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    return chat_service.create_chat(user_id=current_user.id, chat=request, project_id=project_id)

@router.get("/{project_id}/chats", response_model=List[ChatResponse])
def read_project_chats(
    project_id: int,
    current_user: auth_models.User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    return chat_service.read_my_project_chats(user_id=current_user.id, project_id=project_id)