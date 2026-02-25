from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional, Any, Dict, List

from app.db.session import get_db
from app.modules.auth.models import User
from app.modules.libraries.models import TemplateLibrary
from app.modules.libraries.service import TemplateLibraryService
from app.modules.auth.dependencies import get_current_user

from app.modules.templates.schemas import TemplateResponse

from app.modules.libraries.schemas import LibraryResponse, LibraryCreateRequest

router = APIRouter()

@router.get("")
def list_libraries(query: Optional[str] = None, industry: Optional[str] = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Pobiera biblioteki (globalne oraz prywatne) z opcją wyszukiwania."""
    libraries = TemplateLibraryService.get_libraries(db=db, query=query, user_id=current_user.id)
    
    if industry:
        libraries = [lib for lib in libraries if lib.industry == industry]
        
    return libraries

@router.post("", response_model=LibraryResponse)
def create_library(
    request: LibraryCreateRequest, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):
    """Tworzy nową bibliotekę szablonów."""
    new_lib = TemplateLibrary(
        name=request.name,
        industry=request.industry,
        description=request.description,
        is_global=request.is_global,
        creator_id=current_user.id
    )
    db.add(new_lib)
    db.commit()
    db.refresh(new_lib)
    return new_lib

@router.post("/{library_id}/copy")
def copy_library_to_workspace(library_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
    """Najważniejszy endpoint: klonuje całą bibliotekę i jej drzewa AST do przestrzeni użytkownika."""
    newlib_id = TemplateLibraryService.copy_library_to_workspace(db=db, library_id=library_id, user_id=current_user.id)
    return {"message": "Biblioteka skopiowana pomyślnie", "new_library_id": newlib_id}

@router.get("/{library_id}/templates", response_model=List[TemplateResponse])
def get_templates_for_library_id(
    library_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    templates = TemplateLibraryService.get_templates_for_library_id(library_id=library_id, db=db, user_id=current_user.id)
    return templates

@router.post("/{library_id}/add/{template_id}")
def add_template_to_library(
    library_id: int, 
    template_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    TemplateLibraryService.add_template_to_library(db, library_id, template_id, current_user.id)
    return {"message": "Szablon dodany do biblioteki."}

@router.delete("/{library_id}/templates/{template_id}")
def remove_template_from_library(
    library_id: int, 
    template_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    TemplateLibraryService.remove_template_from_library(db, library_id, template_id, current_user.id)
    return {"message": "Szablon odpięty."}