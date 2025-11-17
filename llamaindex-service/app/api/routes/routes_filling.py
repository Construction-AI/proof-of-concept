from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.api.services.filling import list_fields_in_schema
from app.core.schema_types import SchemaType

router = APIRouter()

class FillingRequest(BaseModel):
    type: str

@router.get("/list_schemas")
def route_list_available_schema_types():
    try:
        res = SchemaType.list_available_schema_types()
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/list_fields")
def route_list_fields_in_schema(req: FillingRequest):
    try:
        res = list_fields_in_schema(type_name=req.type)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
