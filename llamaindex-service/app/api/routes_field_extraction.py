from fastapi import APIRouter, HTTPException
from app.core.structured_output import FillFieldRequest, FillFieldResponse, FillAllFieldsRequest, FillAllFieldsResponse
from app.services.field_service import process_field_extraction, process_fill_all_fields

router = APIRouter()

@router.post("", response_model=FillFieldResponse)
async def fill_field(req: FillFieldRequest):
    try:
        return await process_field_extraction(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/all", response_model=FillAllFieldsResponse)
async def fill_all_fields(req: FillAllFieldsRequest):
    try:
        return await process_fill_all_fields(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))