from pydantic import BaseModel, Field
from typing import List

class QueryDocsRequest(BaseModel):
    question: str
    document_ids: List[int]
    
class QueryProjectRequest(BaseModel):
    question: str
    project_id: int

class AnswerWithConfidence(BaseModel):
    answer: str = Field(..., description="The detailed answer to the user's question based on the context.")
    confidence_score: float = Field(..., description="A score from 0.0 to 1.0 indicating how confident you are that the context fully answers the question.")
    reasoning: str = Field(..., description="A brief explanation of why you gave this answer.")

class QueryResponse(BaseModel):
    response: str

class FinalResponse(BaseModel):
    structured_answer: AnswerWithConfidence
    sources: List[str]