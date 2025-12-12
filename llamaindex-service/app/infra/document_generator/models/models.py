from pydantic import BaseModel
from typing import List

class SchemaGroupField(BaseModel):
    key: str
    type: str
    required: bool
    prompt: str
    value: str | None

class SchemaProjectGroup(BaseModel):
    group_id: str
    group_name: str
    fields: List[SchemaGroupField]

class SchemaProjectSchema(BaseModel):
    company_id: str
    project_id: str
    schema_type_name: str
    date_created: str
    
    groups: List[SchemaProjectGroup]
    
    