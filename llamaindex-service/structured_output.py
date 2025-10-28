from pydantic import Field, BaseModel

class FieldExtraction(BaseModel):
    value: str | None = Field(None, description="Extracted value as text; null if not found")
    confidence: float = Field(0.0, ge=0.0, le=1.0, description="Model self-reported confidence 0..1")

class FillFieldRequest(BaseModel):
    project_id: str
    field_id: str
    instruction: str # eg. "Give me the concrete class"
    top_k: int = 8

class FillFieldResponse(BaseModel):
    field_id: str
    value: str | None
    confidence: float
    sources: list

