from fastapi import APIRouter, HTTPException, status
from fastapi.responses import Response

from app.infra.knowledge_base.requests import KnowledgeBaseRequest
from app.infra.knowledge_base.instances_knowledge_base import RagKnowledgeBase, get_rag_knowledge_base
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
        
        knowledge_base = get_rag_knowledge_base()
        await knowledge_base.add_document(file=file)
        return Response(
            status_code=status.HTTP_201_CREATED,
        )
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# @router.get("/query")