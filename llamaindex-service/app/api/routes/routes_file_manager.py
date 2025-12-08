from fastapi import APIRouter, HTTPException
from app.infra.instances_file_manager import get_file_manager, FileUploadRequest

router = APIRouter()

@router.post("/upload")
def route_upload_file(req: FileUploadRequest):
    try:
        file_manager = get_file_manager()
        file_manager.upload_file(req.bucket_name, req.file_path, None)
        return "Success"
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))