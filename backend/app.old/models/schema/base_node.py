from pydantic import BaseModel
from typing import Literal, List

class SchemaBaseNode(BaseModel):    
    id: str
    type: Literal["document", "section", "subsection", "heading", "paragraph", "list", "list_item", "table", "field", "repeat", "conditional"]
