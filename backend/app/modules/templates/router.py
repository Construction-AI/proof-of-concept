# GET /api/v1/templates/ – pobiera listę szablonów (do wyświetlenia biblioteki).

# POST /api/v1/templates/ – tworzy nowy, pusty szablon (tylko nazwę i opis).

# GET /api/v1/templates/{id}/nodes – pobiera listę płaskich węzłów dla danego szablonu.

# PUT /api/v1/templates/{id}/nodes – zapisuje całą zaktualizowaną listę węzłów (zastępuje starą strukturę nową, gdy użytkownik kliknie "Zapisz" w edytorze).

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from schemas import SchemaNode
from service import TemplateService

from app.db.session import get_db

router = APIRouter()

@router.put("/{template_id}/nodes", response_model=List[SchemaNode])
def update_template_nodes(
    template_id: int,
    nodes: List[SchemaNode],
    db: Session = Depends(get_db)
):
    saved_db_nodes = TemplateService.save_template_tree(db=db, template_id=template_id, incoming_nodes=nodes)
    return saved_db_nodes

@router.get("/{template_id}/nodes", response_model=List[SchemaNode])
def read_template_nodes(template_id: int, db: Session = Depends(get_db)):
    return TemplateService.get_template_tree(db=db, template_id=template_id)