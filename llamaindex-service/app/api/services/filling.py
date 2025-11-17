from app.core.schema_types import SchemaType    
from app.api.services.schema_loader import get_all_fields_from_schema, get_field_def
from app.api.services.document_loader import PROJECT_ENGINES, WINDOW_POST
from app.core.logger import get_logger

from fastapi import HTTPException

def list_fields_in_schema(type_name: str):
    all_fields = get_all_fields_from_schema(type_name)
    return all_fields

def build_context_snippets(nodes, max_chars_per_snip=600):
    def _snip(txt: str, n=max_chars_per_snip):
        return (txt[:n] + "..." if txt and len(txt) > n else txt)

    parts = []
    for i, sn in enumerate(nodes, start=1):
        node = sn.node if hasattr(sn, "node") else sn
        meta = node.metadata or {}
        file_name = meta.get("file_name")
        page_label = meta.get("source")
        parts.append(
            f"[{i}] file={file_name} page={page_label}\n{_snip(sn.node.get_content())}"
        )
        
    return "\n\n---\n\n".join(parts)

async def process_field_extraction(project_id: str, field_id: str):
    INSTRUCTION = f"Podaj '{field_id}'" # TODO: Move arbitrarily somewhere else
    TOP_K = 6
    logger = get_logger("Field Extraction")

    if not project_id in PROJECT_ENGINES:
        raise HTTPException(status_code=400, detail=f"No index for project_id='{project_id}'. Create it first.")
    
    try:
        field_def = get_field_def(field_id)
        if not field_def:
            raise HTTPException(status_code=400, detail=f"Unknown field_id: '{field_id}'")
        
        project_engine = PROJECT_ENGINES[project_id]
        nodes = await project_engine.retriever.aretrieve(INSTRUCTION)

        windowed_nodes = WINDOW_POST.postprocess_nodes(nodes, query_str=instruction)

        top_nodes = windowed_nodes[:TOP_K]
        context = build_context_snippets(top_nodes, max_chars_per_snip=1500)

        # program = make_extraction_program()

    except Exception as e:
        logger.error(f"Failed to extract field '{field_id}': {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
