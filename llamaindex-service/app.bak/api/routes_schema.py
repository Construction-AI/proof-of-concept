from fastapi import APIRouter, Query
from app.services.schema_service import load_schema, flatten_fields

router = APIRouter()

@router.get("")
async def get_schema():
    return load_schema()

@router.get("/fields")
async def list_fields():
    return flatten_fields()

@router.get("/fields/search")
async def search_fields(q: str = Query("", min_length=1)):
    ql = q.lower()
    reg = flatten_fields()
    return [f for f in reg if ql in f["field_id"].lower() or ql in (f.get("label") or "").lower()][:200]