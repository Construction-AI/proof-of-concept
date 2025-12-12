from fastapi import APIRouter, HTTPException, status
from fastapi.responses import Response

from app.infra.knowledge_base.requests import KnowledgeBaseRequest
from app.infra.knowledge_base.instances_knowledge_base import KnowledgeBaseWrapper, get_knowledge_base_wrapper
from app.models.files import KBFile

router = APIRouter()

@router.post("/upload")
async def route_upload_document(req: KnowledgeBaseRequest.AddDocument):
    try:
        file = KBFile(
            company_id=req.company_id,
            project_id=req.project_id,
            document_category=req.document_category,
            document_type=req.document_type,
            local_path=req.local_path
        )
        
        knowledge_base = get_knowledge_base_wrapper()
        await knowledge_base.upload_document(file=file)
        return Response(
            status_code=status.HTTP_201_CREATED,
        )
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/query")
async def route_query(req: KnowledgeBaseRequest.Query):
    try:
        knowledge_base = get_knowledge_base_wrapper()
        response = await knowledge_base.query(question=req.question, company_id=req.company_id, 
                                              project_id=req.project_id, document_type=req.document_type, 
                                              document_category=req.document_category, file_name=req.file_name
                                              )
        
        return Response(
            status_code=200,
            content=response.response
        )
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        
@router.post("/delete")
async def route_delete_document(req: KnowledgeBaseRequest.Delete):
    try:
        knowledge_base = get_knowledge_base_wrapper()
        await knowledge_base.delete_document(
            company_id=req.company_id,
            project_id=req.project_id,
            document_category=req.document_category,
            document_type=req.document_type
        )
        return Response(
            status_code=200,
        )
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        
@router.post("/upsert")
async def route_upsert_document(req: KnowledgeBaseRequest.AddDocument):
    try:
        file = KBFile(
            company_id=req.company_id,
            project_id=req.project_id,
            document_category=req.document_category,
            document_type=req.document_type,
            local_path=req.local_path
        )
        
        knowledge_base = get_knowledge_base_wrapper()
        await knowledge_base.upsert_document(file=file)
        return Response(
            status_code=status.HTTP_201_CREATED,
        )
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        
