from functools import lru_cache
from app.models.schema_types import SchemaType
import json

@lru_cache(maxsize=1)
def load_schema(schema_type: SchemaType):
    path = schema_type.get_path()
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)