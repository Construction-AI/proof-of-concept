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
