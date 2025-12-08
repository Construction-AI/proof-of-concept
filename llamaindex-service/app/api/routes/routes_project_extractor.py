from fastapi import APIRouter, HTTPException
from app.api.services.projet_extractor import extract_project_info

router = APIRouter()

@router.get("/{project_id}")
async def route_fill_field(project_id: str):
    try:
        return await extract_project_info(project_id=project_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))