from pydantic import BaseModel, Field, ConfigDict
from typing import Literal, Annotated, Union, Optional
from enum import Enum

class NodeType(str, Enum):
    SECTION = "section"
    LIST = "list"

class SectionData(BaseModel):
    title: str
    show_title: bool = True
    heading_level: int = Field(default=1, ge=1, le=6)
    page_before_break: bool = True
    
class ListData(BaseModel):
    list_type: Literal["bullet", "numbered"] = "bullet"
    spacing: Literal["compact", "normal", "relaxed"] = "normal"
    
class BaseSchemaNode(BaseModel):
    id: str
    parent_id: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)
    
class SectionNode(BaseSchemaNode):
    type: Literal[NodeType.SECTION]
    data: SectionData
    
class ListNode(BaseSchemaNode):
    type: Literal[NodeType.LIST]
    data: ListData
    
SchemaNode = Annotated[
    Union[SectionNode, ListNode],
    Field(discriminator="type")
]