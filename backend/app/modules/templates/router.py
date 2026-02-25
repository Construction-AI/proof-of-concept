from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.modules.templates.schemas import SchemaNode, TemplateResponse, TemplateCreateRequest
from app.modules.templates.service import TemplateService

from app.db.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User


router = APIRouter()

@router.post("", response_model=TemplateResponse)
def create_template(
    request: TemplateCreateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
  return TemplateService.create_template(db=db, name=request.name, user_id=user.id, description=request.description)

@router.put("/{template_id}/nodes", response_model=List[SchemaNode])
def update_template_nodes(
    template_id: int,
    nodes: List[SchemaNode],
    db: Session = Depends(get_db)
):
    saved_db_nodes = TemplateService.save_template_tree(db=db, template_id=template_id, incoming_nodes=nodes)
    return saved_db_nodes

@router.get("", response_model=List[TemplateResponse])
async def read_my_template_nodes(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    try:
        templates = TemplateService.get_templates_for_user_id(db=db, user_id=user.id)
        return [TemplateResponse.model_validate(t) for t in templates]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/{template_id}/nodes", response_model=List[SchemaNode])
def read_template_nodes(template_id: int, db: Session = Depends(get_db)):
    return TemplateService.get_template_tree(db=db, template_id=template_id)

@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return TemplateService.delete_template(db=db, template_id=template_id, user_id=current_user.id)
    
    
# POST /api/v1/templates/{id}/copy
@router.post("/{template_id}/copy", response_model=TemplateResponse)
def copy_template(    
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return TemplateService.copy_template(db=db, template_id=template_id, user_id=current_user.id)