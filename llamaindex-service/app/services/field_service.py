from fastapi import HTTPException
from llama_index.core.program import LLMTextCompletionProgram
from llama_index.core.output_parsers import PydanticOutputParser
from llama_index.core.postprocessor import MetadataReplacementPostProcessor

from app.core.structured_output import FieldExtraction, FillFieldRequest, FillFieldResponse, FillAllFieldsRequest, FillAllFieldsResponse
from app.services.index_service import retrievers
from app.core.schema_loader import get_field_def
from app.core.llama_settings import Settings

from app.services.schema_service import flatten_fields


WINDOW_POST = MetadataReplacementPostProcessor(target_metadata_key="window")

def extract_context_around_value(nodes, extracted_value, context_sentences=3):
    """
    Find where the extracted value appears in the nodes and return surrounding context.

    Args:
        nodes: List of retrieved nodes
        extracted_value: The value that was extracted
        context_sentences: Number of sentences to include before and after

    Returns:
        List of context snippets with metadata
    """

    def search_for_value(val: str, nodes) -> list:
        # Convert value to search string
        search_value = str(val).strip()
        if not search_value:
            return []
        
        contexts = []

        for sn in nodes:
            node = sn.node if hasattr(sn, "node") else sn
            content = node.get_content()

            # Try to find the value in the content (case-insensitive)
            if search_value.lower() not in content.lower():
                continue 

            # Split into sentences (simple approach)
            sentences = re.split("r'(?<=[.!?])\s+", content)

            # Find which sentence(s) contain the value
            for i, sentence in enumerate(sentences):
                if search_value.lower() in sentence.lower():
                    # Get context window
                    start_idx = max(0, i - context_sentences)
                    end_idx = min(len(sentences), i + context_sentences + 1)

                    context_window = " ".join(sentences[start_idx:end_idx])

                    meta = node.metadata or {}
                    contexts.append({
                        "file_name": meta.get("file_name"),
                        "page_label": meta.get("source"),
                        "score": sn.score,
                        "context": context_window,
                        "highlighted_sentence": sentence
                    })
                    break # Found in this node, move to then next node
        return contexts

    import re
    if not extracted_value or extracted_value == "null" or extracted_value == "error":
        return []
    
    all_contexts = []
    
    if type(extracted_value) == list:
        for single_ex_val in extracted_value:
            found_values = search_for_value(single_ex_val, nodes)
            if len(found_values) > 0:
                [all_contexts.append(value) for value in found_values]
    else:
        found_values = search_for_value(extracted_value, nodes)
        [all_contexts.append(value) for value in found_values]

    
    

    return all_contexts


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

async def process_field_extraction(req: FillFieldRequest):
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
        nodes = await fusion.aretrieve(req.instruction)

        # apply sentence-window replacement
        windowed_nodes = WINDOW_POST.postprocess_nodes(nodes, query_str=req.instruction)

        # 2) Build context
        top_nodes = windowed_nodes[: req.top_k]
        context = build_context_snippets(top_nodes, max_chars_per_snip=1500)

        # 3) Run extraction
        program = make_extraction_program()

        result: FieldExtraction = await program.acall(
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
                if field_def.get("type") == "array" or field_def.get("type") == "array_string":
                    extracted_value = unique_values
                else:
                    extracted_value = unique_values[0]

        value_contexts = extract_context_around_value(
            top_nodes,
            extracted_value,
            context_sentences=2
        )

        # 5) Build sources
        src = []
        if value_contexts:
            # Use the smart context extraction
            for ctx in value_contexts:
                src.append({
                    "file_name": ctx["file_name"],
                    "page_label": ctx["page_label"],
                    "score": ctx["score"],
                    "excerpt": ctx["context"], # Context around the value
                    "highlighted": ctx["highlighted_sentence"]

                })
        else:
            # Fallback to original method if value not found
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

async def process_fill_all_fields(req: FillAllFieldsRequest):
    pid = req.project_id
    if not pid in retrievers:
        raise HTTPException(status_code=400, detail=f"No index for project_id='{pid}'. Create it with /index.")
    
    flattened_fields = flatten_fields()
    all_fields = {}
    for field in flattened_fields:
        field_id = field.get("field_id")
        request = FillFieldRequest(
            project_id=req.project_id,
            field_id=field_id,
            instruction=f"Podaj mi {field_id}"
        )
        try:
            response = await process_field_extraction(request)
            all_fields[field_id] = response.value
        except Exception as e:
            print(f"Failed to parse field: '{field_id}'")
            all_fields[field_id] = "error"

    return FillAllFieldsResponse(
        fields=all_fields
    )


