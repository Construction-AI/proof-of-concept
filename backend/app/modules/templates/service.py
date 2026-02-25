from typing import List, Optional
from sqlalchemy.orm import Session
from app.modules.templates.schemas import SchemaNode
from app.modules.templates.models import TemplateNodes, Template

class TemplateService:
    @staticmethod
    def save_template_tree(db: Session, template_id: int, incoming_nodes: List[SchemaNode]):
        db.query(TemplateNodes).filter(TemplateNodes.template_id == template_id).delete()
        
        db_nodes: List[TemplateNodes] = []
        
        for node in incoming_nodes:
            db_node = TemplateNodes(
                id=node.id,
                template_id=template_id,
                parent_id=node.parent_id,
                type=node.type,
                data=node.data.model_dump()
            )
            db_nodes.append(db_node)
            
        db.add_all(db_nodes)
        db.commit()
        return db_nodes
    
    @staticmethod
    def get_template_tree(db: Session, template_id: int) -> List[TemplateNodes]:
        return db.query(TemplateNodes).filter(TemplateNodes.template_id == template_id).all()
    
    @staticmethod
    def get_template_by_id(db: Session, template_id: int, user_id: int) -> Template:
        template: Template = db.query(Template).filter(Template.id == template_id).first()
        if not template or template.owner_id != user_id:
            raise Exception("Template not found or belongs to another user")
        return template
    
    @staticmethod
    def get_templates_for_user_id(db: Session, user_id: int) -> List[Template]:
        return db.query(Template).filter(Template.owner_id == user_id).all()
    
    @staticmethod
    def delete_template(db: Session, template_id: int, user_id: int):
        template: Template = TemplateService.get_template_by_id(db=db, template_id=template_id, user_id=user_id)
        if template:
            db.delete(template)
            
    @staticmethod
    def create_template(db: Session, name: str, user_id: int, description: Optional[str] = None):
        db_template = Template(
            name=name,
            description=description,
            owner_id=user_id
        )
        db.add(db_template)
        db.commit()
        db.refresh(db_template)
        return db_template
    
    @staticmethod
    def copy_template(template_id: int, db: Session, user_id: int):
        og_template = TemplateService.get_template_by_id(db=db, template_id=template_id, user_id=user_id)
        
        new_template = Template(
            name=og_template.name,
            description=og_template.description,
            owner_id=user_id
        )
        
        db.add(new_template)
        db.flush()

        # 3. Klonowanie klocków z zachowaniem relacji parent-child (SŁOWNIK MAPUJĄCY)
        og_nodes = db.query(TemplateNodes).filter(TemplateNodes.template_id == og_template.id).all()
        id_map: dict[str, str] = {} # Mapuje stare ID na nowe ID
        
        # Etap A: Tworzymy nowe klocki i zapisujemy ich mapowanie
        for node in og_nodes:
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
        for node in og_nodes:
            if node.parent_id:
                new_node_id: str = id_map[str(node.id)]
                new_parent_id: str = id_map[str(node.parent_id)]
                
                cloned_node = db.query(TemplateNodes).filter(TemplateNodes.id == int(new_node_id)).first()
                if cloned_node:
                    cloned_node.parent_id = new_parent_id
                    
        db.refresh(new_template)
        return new_template
