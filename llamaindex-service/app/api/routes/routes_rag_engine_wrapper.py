from fastapi import APIRouter, HTTPException, status

from app.infra.instances_rag_engine_wrapper import RagEngineWrapper, get_rag_engine_wrapper

router = APIRouter()

@router.post("/load")
def route_load_document(req: RagEngineWrapper.RequestLoadDocument):
    try:
        rag_engine_wrapper = get_rag_engine_wrapper()
        file = RagEngineWrapper.File(
            company_id=req.company_id,
            project_id=req.project_id,
            document_category=req.document_category,
            local_path=req.local_path,
            document_type=req.document_type
        )
        doc = rag_engine_wrapper.load_document(file)
        print(doc)
        return "ok"
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))