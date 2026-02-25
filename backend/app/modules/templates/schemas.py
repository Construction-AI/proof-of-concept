from pydantic import BaseModel, Field, ConfigDict
from typing import Literal, Annotated, Union, Optional
from enum import Enum

class NodeType(str, Enum):
    SECTION = "section"
    LIST = "list"
    STATIC_TEXT = "static_text"
    RAG_EXTRACTION = "rag_extraction"
    
class BaseSchemaNode(BaseModel):
    id: str
    parent_id: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

# -- Section -- 
class SectionData(BaseModel):
    title: str
    show_title: bool = True
    heading_level: int = Field(default=1, ge=1, le=6)
    page_before_break: bool = True
    
class SectionNode(BaseSchemaNode):
    type: Literal[NodeType.SECTION]
    data: SectionData
    
# -- List -- 
class ListData(BaseModel):
    list_type: Literal["bullet", "numbered"] = "bullet"
    spacing: Literal["compact", "normal", "relaxed"] = "normal"
    
class ListNode(BaseSchemaNode):
    type: Literal[NodeType.LIST]
    data: ListData
    
# -- Static Text -- 
class StaticTextData(BaseModel):
    text: str
    
class StaticTextNode(BaseSchemaNode):
    type: Literal[NodeType.STATIC_TEXT]
    data: StaticTextData
    
# -- Rag Extraction Data -- 
class RagExtractionData(BaseModel):
    prompt: str
    fallback_text: str
    
class RagExtractionNode(BaseSchemaNode):
    type: Literal[NodeType.RAG_EXTRACTION]
    data: RagExtractionData
    
SchemaNode = Annotated[
    Union[SectionNode, ListNode, StaticTextNode, RagExtractionNode],
    Field(discriminator="type")
]

# !-- Responses --!
from datetime import datetime

class TemplateCreateRequest(BaseModel):
    name: str
    description: str

class TemplateResponse(BaseModel):
    id: int
    name: str
    description: str | None
    owner_id: int
    created_at: datetime
    last_modified: datetime
    model_config = ConfigDict(from_attributes=True)