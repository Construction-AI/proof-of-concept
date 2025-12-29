from fastapi import APIRouter, HTTPException
from app.infra.file_storage.instances_file_storage_wrapper import get_file_storage_wrapper, FileStorageWrapper
from app.infra.file_storage.requests import FileStorageRequest
from app.models.files import FSFile, LocalFile
from fastapi.responses import FileResponse, Response
from fastapi import status

import json

router = APIRouter()

@router.post("/upload")
def route_upload_file(req: FileStorageRequest.Upload):
    try:
        file_manager = get_file_storage_wrapper()
        target_file = LocalFile(
            company_id=req.company_id,
            project_id=req.project_id,
            document_category=req.document_category,
            local_path=req.local_file_path,
            document_subtype="raw" # TODO: Change this
        )
        file_url = file_manager.upload_file(local_file=target_file)
        return Response(status_code=status.HTTP_201_CREATED, content=json.dumps({"file_url": file_url}))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
@router.post("/upsert")
def route_upsert_file(req: FileStorageRequest.Upsert):
    try:
        file_manager = get_file_storage_wrapper()

        # We can use the same for both old and new file, since the file location is the same (and file name)
        target_file = LocalFile(
            company_id=req.company_id,
            project_id=req.project_id,
            document_category=req.document_category,
            local_path=req.local_file_path
        )
        file_url = file_manager.upsert_file(
            target_file=target_file
        )
        return Response(status_code=status.HTTP_201_CREATED,
                        content=json.dumps({"file_url": file_url}),
                        media_type="application/json"
                )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    
@router.post("/delete")
def route_delete_file(req: FileStorageRequest.Delete):
    try:
        file_manager = get_file_storage_wrapper()
        target_file = FSFile(
            company_id=req.company_id,
            project_id=req.project_id,
            document_category=req.document_category
        )
        file_manager.delete_file(target_file=target_file)
        return Response(
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
@router.get("/read/{company_id}/{project_id}/{document_category}/{document_type}")
def route_read_file(company_id: str, project_id: str, document_category: str, document_type: str):
    try:
        file_manager = get_file_storage_wrapper()
        target_file = FSFile(
            company_id=company_id,
            project_id=project_id,
            document_category=document_category,
            document_type=document_type
        )        
        target_file, temp_path = file_manager.read_file(target_file=target_file)
        if not temp_path:
            raise f"Failed to read from file: {target_file.remote_file_path}"
        response = FileResponse(path=temp_path, filename=target_file.file_name)
        return response
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))