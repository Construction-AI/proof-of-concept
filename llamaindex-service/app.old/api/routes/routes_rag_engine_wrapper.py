from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse, Response

from app.infra.rag_engine.instances_rag_engine_wrapper import RagEngineWrapper, get_rag_engine_wrapper
from app.infra.rag_engine.requests import RagEngineRequest
from app.models.files import LocalFile, FSFile

router = APIRouter()

@router.post("/upload_document")
async def route_upload_document(req: RagEngineRequest.UploadDocument):
    try:
        rag_engine_wrapper = get_rag_engine_wrapper()
        file = LocalFile(
            company_id=req.company_id,
            project_id=req.project_id,
            document_category=req.document_category,
            local_path=req.local_file_path
        )
        
        await rag_engine_wrapper.upload_document(file=file)
        return Response(
            status_code=status.HTTP_201_CREATED,
        )
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/upsert_document")
async def route_upsert_document(req: RagEngineRequest.UpsertDocument):
    try:
        rag_engine_wrapper = get_rag_engine_wrapper()
        file = LocalFile(
            company_id=req.company_id,
            project_id=req.project_id,
            document_category=req.document_category,
            local_path=req.local_file_path
        )
        
        await rag_engine_wrapper.upsert_document(file=file)
        return Response(
            status_code=status.HTTP_201_CREATED,
        )
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
@router.get("/read_document/{company_id}/{project_id}/{document_category}/{document_type}")
def route_read_document(company_id: str, project_id: str, document_category: str, document_type: str):
    try:
        rag_engine_wrapper = get_rag_engine_wrapper()
        file = FSFile(
            company_id=company_id,
            project_id=project_id,
            document_category=document_category,
            document_type=document_type
        )
        
        file, tmp_file_path = rag_engine_wrapper.read_document(file=file)
        if not tmp_file_path:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Failed to read from file: {file.remote_file_path}")
        response = FileResponse(path=tmp_file_path, filename=file.file_name)
        return response
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
    
@router.post("/delete_document")
async def route_delete_document(req: RagEngineRequest.DeleteDocument):
    try:
        rag_engine_wrapper = get_rag_engine_wrapper()
        file = FSFile(
            company_id=req.company_id,
            project_id=req.project_id,
            document_category=req.document_category
        )
        
        await rag_engine_wrapper.delete_document(file=file)
        return Response(
            status_code=status.HTTP_200_OK,
        )
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
@router.post("/query")
async def route_query(req: RagEngineRequest.QueryKnowledgeBase):
    try:
        rag_engine_wrapper = get_rag_engine_wrapper()
        response = await rag_engine_wrapper.query(question=req.question, company_id=req.company_id, 
                                              project_id=req.project_id, document_type=req.document_type, 
                                              document_category=req.document_category, file_name=req.file_name
                                              )
        
        return Response(
            status_code=200,
            content=response
        )
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
# @router.post("/generate_document")
# async def route_generate_document(req: RagEngineRequest.GenerateDocument):
#     try:
#         rag_engine_wrapper = get_rag_engine_wrapper()
#         generated_file: LocalFile = await rag_engine_wrapper.generate_document(document_type=req.document_category, author=req.author, company_id=req.company_id, project_id=req.project_id)
#         return FileResponse(
#             status_code=200,
#             path=generated_file.local_path,
#             filename=generated_file.file_name
#         )
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        
@router.post("/generate_docx")
async def route_generate_docx(req: RagEngineRequest.GenerateDocx):
    try:
        rag_engine_wrapper = get_rag_engine_wrapper()
        generated_file: str = await rag_engine_wrapper.generate_docx(
            bucket=req.bucket,
            file_url=req.file_url
        )
        from pathlib import Path
        return FileResponse(status_code=200, path=generated_file, filename=Path(generated_file).name)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
