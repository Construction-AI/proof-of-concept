from fastapi import HTTPException
from app.services.index_service import query_engines

def query_documents(project_id: str, query: str):
    if project_id not in query_engines:
        raise HTTPException(status_code=400, detail=f"No index for project '{project_id}'")
    
    qe = query_engines[project_id]
    response = qe.query(query)

    def _snip(txt: str, n=300):
        return (txt[:n] + "...") if txt and len(txt) > n else txt
    
    source_nodes = []
    if hasattr(response, "source_nodes"):
        for sn in response.source_nodes:
            meta = sn.node.metadata or {}
            source_nodes.append({
                "file_name": meta.get("file_name"),
                "page_label": meta.get("page_label"),
                "score": sn.score,
                "excerpt": _snip(sn.node.get_content())
            })

    return {
        "response": str(response),
        "source_nodes": source_nodes
    }