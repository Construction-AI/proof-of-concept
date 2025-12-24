from app.models.schema.basic import SchemaDocument
from app.core.schema.mapper import SchemaMapper

class SchemaEngine:
    @staticmethod
    def parse_schema(data: dict) -> SchemaDocument:
        return SchemaMapper.parse_schema(data=data)
    
    # TODO: TEMPORARY SOLUTION (counting on pydantic errors) - change this
    @staticmethod
    def validate_schema(data: dict) -> bool:
        try:
            SchemaMapper.parse_schema(data=data)
            return True
        except:
            return False
        
    @staticmethod
    def generate(doc: SchemaDocument) -> dict:
        import json
        data = json.loads(s=doc.model_dump_json(ensure_ascii=False))
        
    