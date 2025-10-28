from fastapi import APIRouter, HTTPException
from app.core.structured_output import FillFieldRequest, FillFieldResponse
from app.services.field_service import process_field_extraction

router = APIRouter()

@router.post("", response_model=FillFieldResponse)
async def fill_field(req: FillFieldRequest):
    try:
        return process_field_extraction(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))