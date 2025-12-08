from fastapi import APIRouter, HTTPException
from app.infra.instances_file_manager import get_file_manager, FileUploadRequest, FileDeleteRequest

router = APIRouter()

@router.post("/upload")
def route_upload_file(req: FileUploadRequest):
    try:
        file_manager = get_file_manager()
        file_manager.upload_file(req.bucket_name, req.file_path, req.destination_file)
        return "Success"
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/delete")
def route_delete_file(req: FileDeleteRequest):
    try:
        file_manager = get_file_manager()
        file_manager.delete_file(bucket_name=req.bucket_name, target_file=req.target_file)
        return "Success"
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))