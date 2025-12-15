from typing import Optional, List, Union
from pydantic import BaseModel
    
class SchemaBaseElement(BaseModel):
    @staticmethod
    def create(text: Optional[str] = None, list_elements: Optional[List] = None, list_type: Optional[str] = None):
        assert text or list_elements, "Either `text` or `list_elements` is required."
        assert not (text and list_elements), "Cannot use both `text` and `list_elements`."
        if text:
            return SchemaParagraph(text=text)
        elif list_elements:
            if list_type == "numbered":
                return SchemaNumberedList(elements=list_elements)
            elif list_type == "bullet":
                return SchemaBulletList(elements=list_elements)
    

class SchemaFieldExtractionField(SchemaBaseElement):
    extracted_value: Optional[str] = None
    prompt: str
    type: str
    example: Union[str, List[str]]
    
class SchemaParagraph(SchemaBaseElement):
    text: str
            
class SchemaList(SchemaBaseElement):
    heading: SchemaParagraph
    elements: List[SchemaParagraph]
    
class SchemaNumberedList(SchemaList):
    pass
    
class SchemaBulletList(SchemaList):
    pass

class SchemaSubSubsection(BaseModel):
    heading: SchemaParagraph
    description: Optional[SchemaParagraph] = None
    elements: List[Union[SchemaParagraph, SchemaBulletList, SchemaNumberedList, SchemaFieldExtractionField]]

class SchemaSubsection(BaseModel):
    heading: SchemaParagraph
    description: Optional[SchemaParagraph] = None
    subsubsections: List[SchemaSubSubsection]

class SchemaSection(BaseModel):
    new_page: Optional[bool] = False
    heading: SchemaParagraph
    description: Optional[SchemaParagraph] = None
    subsections: List[SchemaSubsection] = []
    
class SchemaTableOfContents(BaseModel):
    sections: List[SchemaSection]

class SchemaMeta(BaseModel):
    # Business data
    company_id: str
    project_id: str
    author: str
    
    # Generation data
    version_id: str
    date_created: str
    date_modified: str
    
    # Document data
    document_type: str
    system_instruction: str
    
class Schema(BaseModel):
    meta: SchemaMeta
    sections: List[SchemaSection] = []
