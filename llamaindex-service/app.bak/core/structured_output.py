from pydantic import Field, BaseModel
from typing import Optional, List, Union, Dict, Any

class FieldExtraction(BaseModel):
    """Result of extracting a single field value from documents"""
    value: Optional[Union[str, List[str]]] = Field(
        default=None,
        description="Extracted value(s). Single string for unique values, list for multiple distinct values"
    )
    confidence: Optional[float] = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence score between 0 and 1"
    )
    reasoning: Optional[str] = Field(
        default=None,
        description="Brief explanation of the extraction"
    )



class FillFieldRequest(BaseModel):
    project_id: str
    field_id: str
    instruction: str # eg. "Give me the concrete class"
    top_k: int = 8

class FillFieldResponse(BaseModel):
    field_id: str
    value: str | list | None
    confidence: float
    sources: list

class FillAllFieldsRequest(BaseModel):
    project_id: str

class FillAllFieldsResponse(BaseModel):
    fields: dict[str, Any]

