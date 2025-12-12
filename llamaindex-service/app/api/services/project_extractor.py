from pydantic import BaseModel
from typing import List
from app.api.services.schema_loader import load_schema
from app.models.schema_types import SchemaType
from app.api.services.rag_engine import query_project
from app.core.logger import get_logger

class GroupField(BaseModel):
    key: str
    type: str
    required: bool
    prompt: str
    value: str | None

class ProjectGroup(BaseModel):
    group_id: str
    group_name: str
    fields: List[GroupField]

class ProjectSchema(BaseModel):
    groups: List[ProjectGroup]

def count_groups(schema: dict) -> int:
    return len(schema)

def count_fields_to_fill(schema: dict) -> int:
    fields_count = 0
    for gr in schema:
        fields_count += len(gr["fields"])

    return fields_count

async def extract_project_info(project_id: str, schema_type: SchemaType):
    logger = get_logger("Extract Project Info")
    schema = load_schema(schema_type.get_key())
    groups_count = count_groups(schema)
    groups = []
    for g_idx, gr in enumerate(schema):
        group = ProjectGroup(
            group_id = gr["group_id"],
            group_name = gr["group_name"],
            fields = []
        )
        fields_count = len(gr["fields"])
        for f_idx, fd in enumerate(gr["fields"]):
            field_value = await query_project(project_id=project_id, question=fd["prompt"])
            field = GroupField(
                key = fd["key"],
                type = fd["type"],
                required = fd["required"],
                prompt = fd["prompt"],
                value = field_value.response
            )
            group.fields.append(field)
            logger.info(f"Filled {f_idx + 1} / {fields_count} fields of group {g_idx + 1}.")
        logger.info(f"Filled {g_idx + 1} / {groups_count} groups.")
        groups.append(group)

    return groups
