from app.models.schema.base_node import SchemaBaseNode
from typing import Literal, Optional, List, Union, Dict

SchemaNode = Union[
    "SchemaDocument",
    "SchemaSection",
    "SchemaSubsection",
    "SchemaHeading",
    "SchemaParagraph",
    "SchemaList",
    "SchemaListItem",
    "SchemaTable",
]

class SchemaField(SchemaBaseNode):    
    type: Literal["field"] = "field"
    
    source: Literal["ai", "user"]
    prompt: Optional[str] = None
    required: Optional[bool] = False
    data_type: Literal["text", "number", "boolean", "date", "list[text]"]

class SchemaDocument(SchemaBaseNode):
    type: Literal["document"] = "document"
    meta: dict
    children: List[SchemaNode]
    fields: Optional[Dict[str, SchemaField]] = {}

class SchemaSection(SchemaBaseNode):
    type: Literal["section"] = "section"
    
    title: str
    children: List[SchemaNode]

class SchemaSubsection(SchemaBaseNode):
    type: Literal["subsection"] = "subsection"
    
    title: str
    children: List[SchemaNode]

class SchemaHeading(SchemaBaseNode):
    type: Literal["heading"] = "heading"
    text: str

class SchemaParagraph(SchemaBaseNode):
    type: Literal["paragraph"] = "paragraph"
    source: Literal["static", "field"]
    field: Optional[str] = None
    content: Optional[str] = None

class SchemaList(SchemaBaseNode):
    type: Literal["list"] = "list"
    children: List[SchemaNode]
    list_type: Literal["numbered", "bulleted"]

class SchemaListItem(SchemaBaseNode):
    type: Literal["list_item"] = "list_item"
    children: List[SchemaNode]
    

class SchemaTable(SchemaBaseNode):
    type: Literal["table"] = "table"

# class SchemaRepeat(SchemaBaseNode):
#     type: Literal["repeat"] = "repeat"

# class SchemaConditional(SchemaBaseNode):
#     type: Literal["conditional"] = "conditional"

