from pydantic import BaseModel

class AllCollectionsResponse(BaseModel):
    status: str
    collections: list