from app.models.schema_types import SchemaType    
from app.api.services.schema_loader import get_all_fields_from_schema, get_field_def
from app.api.services.document_loader import PROJECT_ENGINES, WINDOW_POST
from app.core.logger import get_logger
from llama_index.core.output_parsers import PydanticOutputParser
from llama_index.core.program import LLMTextCompletionProgram

from llama_index.core.settings import Settings

from pydantic import Field, BaseModel
from typing import Optional, Union, List

from fastapi import HTTPException

class FieldExtraction(BaseModel):
    value: Optional[Union[str, List[str]]] = Field(
        default=None,
        description="Extracted value(s). Single string for unique values, list for multiple distinct values"
    )

    confidence: Optional[float] = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence score between 0 and 1"
    )

    reasoning: Optional[str] = Field(
        default=None,
        description="Brief explanation of the extraction"
    )

class FillFieldResponse(BaseModel):
    field_id: str
    value: str | list | None
    confidence: float
    sources: list | None

class FillFieldRequest(BaseModel):
    project_id: str
    field_id: str
    schema_type_name: str
    # instruction: str
    # top_k: int = 8


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
        llm=Settings.llm
    )

    return program

async def process_field_extraction(project_id: str, field_id: str, schema_type_name: str):
    TOP_K = 6
    logger = get_logger("Field Extraction")

    if not project_id in PROJECT_ENGINES:
        raise HTTPException(status_code=400, detail=f"No index for project_id='{project_id}'. Create it first.")
    
    try:
        field_def = get_field_def(schema_type_name, field_id)
        if not field_def:
            raise HTTPException(status_code=400, detail=f"Unknown field_id: '{field_id}'")
        
        INSTRUCTION = f"Podaj '{field_id}'. Dodatkowe dane: {field_def.get('label')}" # TODO: Move arbitrarily somewhere else
        project_engine = PROJECT_ENGINES[project_id]
        nodes = await project_engine.retriever.aretrieve(INSTRUCTION)

        windowed_nodes = WINDOW_POST.postprocess_nodes(nodes, query_str=INSTRUCTION)

        top_nodes = windowed_nodes[:TOP_K]
        context = build_context_snippets(top_nodes, max_chars_per_snip=1500)

        program = make_extraction_program()

        result: FieldExtraction = await program.acall(
            instruction=INSTRUCTION, context=context
        )

        extracted_value = result.value
        if isinstance(extracted_value, list):
            # Remove duplicates
            unique_values = []
            seen = set()
            for v in extracted_value:
                if v not in seen:
                    unique_values.append(v)
                    seen.add(v)
            
            if len(unique_values) == 1:
                extracted_value = unique_values[0]
            else:
                if field_def.get('type') == 'array' or field_def.get('type') == 'array_string':
                    extracted_value = unique_values
                else:
                    extracted_value = unique_values[0]

        # TODO: Add logic to extract contexts
        # TODO: Build sources

        return FillFieldResponse(
            field_id=field_id,
            value=extracted_value,
            confidence=float(result.confidence or 0.0),
            sources=None
        )

    except Exception as e:
        logger.error(f"Failed to extract field '{field_id}': {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
