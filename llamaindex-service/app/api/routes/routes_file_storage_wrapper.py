from fastapi import APIRouter, HTTPException
from app.infra.instances_file_storage_wrapper import get_file_manager, FileUploadRequest, FileDeleteRequest, FileStorageWrapper

router = APIRouter()

@router.post("/upload")
def route_upload_file(req: FileUploadRequest):
    try:
        file_manager = get_file_manager()
        target_file = FileStorageWrapper.File(
            company_id=req.company_id,
            project_id=req.project_id,
            document_category=req.document_category,
            local_path=req.local_file_path
        )
        file_manager.create_file(target_file=target_file)
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