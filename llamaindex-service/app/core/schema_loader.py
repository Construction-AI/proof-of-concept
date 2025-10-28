import json
from functools import lru_cache
import os

SCHEMA_PATH = os.getenv("SCHEMA_PATH", "/app/schema/opis_techniczny_konstrukcja.json")

@lru_cache(maxsize=1)
def load_schema():
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)
    
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
                        # Return a synthetic def for the subfield (treated as string by default)
                        return {
                            "id": f"{f.get('id')}.{k}",
                            "label": f"{f.get('label')} -> {k}",
                            "type": "string"
                            }
    return None
