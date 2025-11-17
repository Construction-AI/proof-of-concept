import json
from functools import lru_cache
import os
from app.core.schema_types import SchemaType

@lru_cache(maxsize=1)
def load_schema(type_name: str):
    path = SchemaType.get_path_for_type_name(type_name=type_name)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
    
def get_all_fields_from_schema(type_name: str):
    schema = load_schema(type_name)
    return flatten_fields(schema)
    
def flatten_fields(schema: dict):
    reg = []
    for sec in schema.get("sections", []):
        sid = sec.get("id")
        for f in sec.get("fields", []):
            base_id = f"{sid}.{f.get('id')}"
            reg.append({
                "field_id": base_id,
                "label": f.get("label"),
                "type": f.get("type"),
                "required": f.get("required", False)
            })

            # expand object subkeys (optional, helps discoverability)
            if f.get("type") == "object" and isinstance(f.get("value"), dict):
                for k in f["value"].keys():
                    reg.append({
                        "field_id": f"{base_id}.{k}",
                        "label": f"{f.get('label')} -> {k}",
                        "type": "subfield",
                        "required": f.get("required", False),
                        "parent": base_id
                    })
    return reg

def get_field_def(field_id: str):
    schema = load_schema()
    for sec in schema.get("sections", []):
        sid = sec.get("id")
        for f in sec.get("fields", []):
            if field_id == f"{sid}.{f.get('id')}":
                return f
            if f.get("type") == "object" and isinstance(f.get("value"), dict):
                for k in f["value"].keys():
                    if field_id == f"{sid}.{f.get('id')}.{k}":
                        return {
                            "id": f"{f.get('id')}.{k}",
                            "label": f"{f.get('label')} -> {k}",
                            "type": "string"
                            }
    return None
