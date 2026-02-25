from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
from fastapi import HTTPException

from app.modules.libraries.models import TemplateLibrary
from app.modules.templates.models import TemplateNodes, Template

class TemplateLibraryService:
    
    @staticmethod
    def get_libraries(db: Session, user_id: int, query: Optional[str] = None):
        # 1. Pobieramy biblioteki użytkownika LUB globalne
        db_query = db.query(TemplateLibrary).filter(
            or_(
                TemplateLibrary.creator_id == user_id, 
                TemplateLibrary.is_global == True
            )
        )
        
        # 2. Jeśli podano query, filtrujemy dodatkowo po nazwie (niezależnie od wielkości liter)
        if query:
            db_query = db_query.filter(TemplateLibrary.name.ilike(f"%{query}%"))
            
        return db_query.all()
    
    @staticmethod
    def copy_library_to_workspace(db: Session, library_id: int, user_id: int):
        original_lib = db.query(TemplateLibrary).filter(TemplateLibrary.id == library_id).first()
        if not original_lib:
            raise HTTPException(status_code=404, detail="Biblioteka nie znaleziona")

        # 1. Klonowanie samej biblioteki
        new_lib = TemplateLibrary(
            name=f"{original_lib.name} (Kopia)",
            industry=original_lib.industry,
            description=original_lib.description,
            is_global=False, # Zawsze staje się prywatna dla klonującego
            creator_id=user_id
        )
        db.add(new_lib)
        db.flush() # Wymusza wygenerowanie new_lib.id bez pełnego commita

        # 2. Klonowanie szablonów wewnątrz biblioteki
        for orig_template in original_lib.templates:
            new_template = Template(
                name=orig_template.name,
                owner_id=user_id # Ustawiamy właściciela zamiast przypisanego library_id
            )
            
            # Powiązanie przez relację wiele-do-wielu:
            new_template.libraries.append(new_lib)
            
            db.add(new_template)
            db.flush()

            # 3. Klonowanie klocków z zachowaniem relacji parent-child (SŁOWNIK MAPUJĄCY)
            orig_nodes = db.query(TemplateNodes).filter(TemplateNodes.template_id == orig_template.id).all()
            id_map: dict[str, str] = {} # Mapuje stare ID na nowe ID
            
            # Etap A: Tworzymy nowe klocki i zapisujemy ich mapowanie
            for node in orig_nodes:
                new_node = TemplateNodes(
                    template_id=new_template.id,
                    type=node.type,
                    data=node.data,
                    parent_id=None # Uzupełnimy w Etapie B
                )
                db.add(new_node)
                db.flush()
                id_map[str(node.id)] = str(new_node.id)

            # Etap B: Odtwarzamy zagnieżdżenia używając nowych ID
            for node in orig_nodes:
                if node.parent_id:
                    new_node_id: str = id_map[str(node.id)]
                    new_parent_id: str = id_map[str(node.parent_id)]
                    
                    cloned_node = db.query(TemplateNodes).filter(TemplateNodes.id == int(new_node_id)).first()
                    if cloned_node:
                        cloned_node.parent_id = new_parent_id

        db.commit()
        return new_lib.id
    
    @staticmethod
    def get_templates_for_library_id(library_id: int, db: Session, user_id: int):        
        library = db.query(TemplateLibrary).filter(TemplateLibrary.id == library_id).first()
        if not library:
            raise HTTPException(status_code=404, detail="Biblioteka nie znaleziona")
        return library.templates # Pobieramy prosto z relacji

    # --- NOWE METODY ---
    @staticmethod
    def add_template_to_library(db: Session, library_id: int, template_id: int, user_id: int):
        library = db.query(TemplateLibrary).filter(TemplateLibrary.id == library_id, TemplateLibrary.creator_id == user_id).first()
        template = db.query(Template).filter(Template.id == template_id).first()
        
        if not library or not template:
            raise HTTPException(status_code=404, detail="Brak obiektu lub uprawnień")

        if template not in library.templates:
            library.templates.append(template)
            db.commit()

    @staticmethod
    def remove_template_from_library(db: Session, library_id: int, template_id: int, user_id: int):
        library = db.query(TemplateLibrary).filter(TemplateLibrary.id == library_id, TemplateLibrary.creator_id == user_id).first()
        template = db.query(Template).filter(Template.id == template_id).first()
        
        if library and template in library.templates:
            library.templates.remove(template)
            db.commit()
