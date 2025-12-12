from fastapi import APIRouter, HTTPException
from app.api.services.project_extractor import extract_project_info
from app.infra.file_storage.instances_file_storage_wrapper import get_file_storage_wrapper
from app.models.schema_types import SchemaType
import json

router = APIRouter()
    
@router.get("/project_info/{project_id}")
async def route_extract_project_info(project_id: str):
    try:
        file_manager = get_file_storage_wrapper()
        filled_schema = await extract_project_info(project_id=project_id, schema_type=SchemaType.BAZA_PROJEKTOWA)
        groups = [group.model_dump() for group in filled_schema]
        file_manager.upload_file_as_content("projects", "opis_konstrukcji/schema.json", json.dumps(groups, indent=2, ensure_ascii=False).encode())
        return filled_schema
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/construction_description/{project_id}")
async def route_extract_construction_description(project_id: str):
    try:
        file_manager = get_file_storage_wrapper()
        filled_schema = await extract_project_info(project_id=project_id, schema_type=SchemaType.OPIS_TECHNICZNY)
        groups = [group.model_dump() for group in filled_schema]
        file_manager.upload_file_as_content("projects", "construction_description/schema.json", json.dumps(groups, indent=2, ensure_ascii=False).encode())
        return filled_schema
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/bioz/{project_id}")
async def route_extract_bioz(project_id: str):
    try:
        file_manager = get_file_storage_wrapper()
        filled_schema = await extract_project_info(project_id=project_id, schema_type=SchemaType.BIOZ)
        groups = [group.model_dump() for group in filled_schema]
        file_manager.upload_file_as_content("projects", "bioz/schema.json", json.dumps(groups, indent=2, ensure_ascii=False).encode())
        return filled_schema
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
