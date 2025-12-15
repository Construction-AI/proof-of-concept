from pydantic import BaseModel, Field
from typing import Optional, Union, List

class FieldExtraction(BaseModel):
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
