from app.models.schema import *

class SchemaGeneratorService:
    def __init__(self, meta: SchemaMeta):
        self.schema: Schema = Schema(meta=meta)
        
    def add_section(self, section: SchemaSection) -> None:
        self.sections.append(section)
        
    def add_subsection(self, parent: SchemaSection, child: SchemaSubsection) -> None:
        parent.subsections.append(child)
        
    def add_subsubsection(
        parent: SchemaSubsection, child: SchemaSubsection) -> None:
        parent.subsubsections.append(child)
        
    def add_element(
        parent: SchemaSubSubsection, child: SchemaBaseElement) -> None:
        parent.elements.append(child)
        
    def serialize(self) -> dict:
        import json
        return json.loads(
            self.schema.model_dump_json(ensure_ascii=False)
        )
        
    @property
    def meta(self) -> SchemaMeta:
        return self.schema.meta
    
    @property
    def sections(self) -> List[SchemaSection]:
        return self.schema.sections