from __future__ import annotations # MUST be at the absolute top
from pydantic import BaseModel, Field
from typing import Literal, Optional, List, Union, Dict, Annotated

class SchemaBaseNode(BaseModel):
    id: str
    type: str # The literal will be strictly enforced by the subclasses

class FieldExtraction(BaseModel):
    status: Optional[str] = None
    confidence: Optional[float] = None

class SchemaField(BaseModel):
    type: Literal["field"] = "field"
    source: Literal["ai", "user"]
    prompt: Optional[str] = None
    required: Optional[bool] = None
    data_type: Literal["text", "number", "boolean", "date", "list[text]"]
    extraction: Optional[FieldExtraction] = None
    value: Optional[str] = None

class SchemaHeading(SchemaBaseNode):
    type: Literal["heading"] = "heading"
    text: str

class SchemaParagraph(SchemaBaseNode):
    type: Literal["paragraph"] = "paragraph"
    source: Literal["static", "field"]
    field: Optional[str] = None
    content: Optional[Union[str, FieldExtraction]] = None

class SchemaListItem(SchemaBaseNode):
    type: Literal["list_item"] = "list_item"
    children: List[SchemaNode] = Field(default_factory=list) # Replaced []

class SchemaList(SchemaBaseNode):
    type: Literal["list"] = "list"
    list_type: Literal["numbered", "bulleted"]
    children: List[SchemaListItem] = Field(default_factory=list)

class SchemaTable(SchemaBaseNode):
    type: Literal["table"] = "table"
    children: List[SchemaNode] = Field(default_factory=list)

class SchemaSubsection(SchemaBaseNode):
    type: Literal["subsection"] = "subsection"
    title: str
    children: List[SchemaNode] = Field(default_factory=list)

class SchemaSection(SchemaBaseNode):
    type: Literal["section"] = "section"
    title: str
    children: List[SchemaNode] = Field(default_factory=list)

# The Discriminated Union (Highly Optimized)
SchemaNode = Annotated[
    Union[
        SchemaSection,
        SchemaSubsection,
        SchemaHeading,
        SchemaParagraph,
        SchemaList,
        SchemaListItem,
        SchemaTable,
    ],
    Field(discriminator="type") # Tells Pydantic exactly how to parse incoming JSON
]

class SchemaDocument(SchemaBaseNode):
    type: Literal["document"] = "document"
    meta: Dict[str, str] = Field(default_factory=dict)
    children: List[SchemaNode] = Field(default_factory=list)
    fields: Dict[str, SchemaField] = Field(default_factory=dict)
    
# Rebuild the models so Pydantic can map the recursive tree
SchemaListItem.model_rebuild()
SchemaList.model_rebuild()
SchemaTable.model_rebuild()
SchemaSubsection.model_rebuild()
SchemaSection.model_rebuild()
SchemaDocument.model_rebuild()