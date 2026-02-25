from pydantic import BaseModel

class GenerateRequest(BaseModel):
    project_id: int
    template_id: int
        