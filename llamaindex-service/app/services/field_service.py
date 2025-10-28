from fastapi import HTTPException
from llama_index.core.program import LLMTextCompletionProgram
from llama_index.core.output_parsers import PydanticOutputParser
from llama_index.core.postprocessor import MetadataReplacementPostProcessor

from app.core.structured_output import FieldExtraction, FillFieldRequest, FillFieldResponse
from app.services.index_service import retrievers
from app.core.schema_loader import get_field_def
from app.core.llama_settings import Settings

WINDOW_POST = MetadataReplacementPostProcessor(target_metadata_key="window")

def make_extraction_program():
    parser = PydanticOutputParser(output_cls=FieldExtraction)
    template = (
        "You are an extraction assistant. Use only the Context to answer.\n"
        "Task: {instruction}\n\n"
        "IMPORTANT RULES:\n"
        "- If the field appears with the SAME value multiple times, return that single value as a string\n"
        "- If the field appears with DIFFERENT values, return them as a list\n"
        "- If the field is not found or uncertain, set value=null and confidence=0\n"
        "- Set confidence between 0.0 (uncertain) and 1.0 (certain)\n"
        "- Provide brief reasoning for your extraction\n\n"
        "Return strictly a JSON matching the schema: FieldExtraction(value, confidence, reasoning).\n\n"
        "Context:\n{context}\n"
    )
    program = LLMTextCompletionProgram.from_defaults(
        output_parser=parser,
        prompt_template_str=template,
        llm=Settings.llm,
    )
    return program

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

def process_field_extraction(req: FillFieldRequest):
    pid = req.project_id
    if not pid in retrievers:
        raise HTTPException(status_code=400, detail=f"No index for project_id='{pid}'. Create it with /index.")
    try:
        # 0) Check if field exists
        field_def = get_field_def(req.field_id)
        if not field_def:
            raise HTTPException(status_code=400, detail=f"Unknown field_id: {req.field_id}")

        # 1) Retrieve and rerank
        fusion = retrievers[pid]
        nodes = fusion.retrieve(req.instruction)

        # apply sentence-window replacement
        windowed_nodes = WINDOW_POST.postprocess_nodes(nodes, query_str=req.instruction)

        # 2) Build context
        top_nodes = windowed_nodes[: req.top_k]
        context = build_context_snippets(top_nodes, max_chars_per_snip=1500)

        # 3) Run extraction
        program = make_extraction_program()
        result: FieldExtraction = program(
            instruction=req.instruction, context=context
        )

        # 4) Normalize the value - if it's a list with all same values, pick the first one
        extracted_value = result.value
        if isinstance(extracted_value, list):
            # Remove duplicates while preserving order
            unique_values = []
            seen = set()
            for v in extracted_value:
                if v not in seen:
                    unique_values.append(v)
                    seen.add(v)
            
            # If all values are the same (or only one unique), return single value
            if len(unique_values) == 1:
                extracted_value = unique_values[0]
            else:
                # Multiple different values - you could either:
                # 1. Return the first one (most common/highest confidence)
                # 2. Join them (e.g., "C25/30, C8/10")
                # 3. Keep as list if FillFieldResponse supports it
                extracted_value = unique_values[0]  # Take the most relevant (first retrieved)
                print(f"Warning: Multiple different values found for {req.field_id}: {unique_values}")

        # 5) Build sources
        src = []
        for sn in top_nodes:
            meta = sn.node.metadata or {}
            content = sn.node.get_content() or ""
            excerpt = content if len(content) <= 2000 else (content[:2000] + "...")
            
            src.append({
                "file_name": meta.get("file_name"),
                "page_label": meta.get("source"),
                "score": sn.score,
                "excerpt": excerpt
            })
        
        return FillFieldResponse(
            field_id=req.field_id,
            value=extracted_value,
            confidence=float(result.confidence or 0.0),
            sources=src
        )
    except Exception as e:
        print(f"Error in /fill_field: {e}")
        raise HTTPException(status_code=500, detail=str(e))