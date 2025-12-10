from fastapi import APIRouter, HTTPException
from app.infra.instances_file_storage_wrapper import get_file_storage_wrapper, FileUploadRequest, FileDeleteRequest, FileStorageWrapper
from fastapi.responses import FileResponse, Response
from fastapi import status

import json

router = APIRouter()

@router.post("/upload")
def route_upload_file(req: FileUploadRequest):
    try:
        file_manager = get_file_storage_wrapper()
        target_file = FileStorageWrapper.File(
            company_id=req.company_id,
            project_id=req.project_id,
            document_category=req.document_category,
            local_path=req.local_file_path
        )
        file_url = file_manager.create_file(target_file=target_file)
        return Response(status_code=status.HTTP_201_CREATED, content={
            "file_url": file_url
        })
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
@router.post("/upsert")
def route_upsert_file(req: FileUploadRequest):
    try:
        file_manager = get_file_storage_wrapper()

        # We can use the same for both old and new file, since the file location is the same (and file name)
        target_file = FileStorageWrapper.File(
            company_id=req.company_id,
            project_id=req.project_id,
            document_category=req.document_category,
            local_path=req.local_file_path
        )
        file_url = file_manager.upsert_file(
            old_file=target_file,
            new_file=target_file
        )
        return Response(status_code=status.HTTP_201_CREATED,
                        content=json.dumps({"file_url": file_url}),
                        media_type="application/json"
                )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    
@router.post("/delete")
def route_delete_file(req: FileDeleteRequest):
    try:
        file_manager = get_file_storage_wrapper()
        file_manager.delete_file(bucket_name=req.bucket_name, target_file=req.target_file)
        return Response(
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
@router.get("/read/{company_id}/{project_id}/{document_category}/{document_type}/{file_name}")
def route_read_file(company_id: str, project_id: str, document_category: str, document_type: str, file_name: str):
    try:
        file_manager = get_file_storage_wrapper()
        target_file = FileStorageWrapper.File(
            company_id=company_id,
            project_id=project_id,
            document_category=document_category,
            document_type=document_type,
            read_file_name=file_name
        )
        tmp_file_path = file_manager.read_file(target_file=target_file)
        if not tmp_file_path:
            raise f"Failed to read from file: {target_file.remote_file_path}"
        return FileResponse(path=tmp_file_path, filename=file_name)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))