from typing import List
from sqlalchemy.orm import Session

from app.modules.templates.schemas import SchemaNode
from app.modules.templates.models import TemplateNodes

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
        return db.query(TemplateNodes).filter(TemplateNodes.id == template_id).all()