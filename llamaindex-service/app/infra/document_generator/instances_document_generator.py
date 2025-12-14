from app.infra.document_generator.loaders.loader import load_schema
from app.core.logger import get_logger
from app.infra.document_generator.models.models import *
from app.infra.knowledge_base.instances_knowledge_base import get_knowledge_base_wrapper
import datetime
from app.core.document_mapper import DocumentMapper

class DocumentGenerator:
    def __init__(self):
        pass
    
    class SchemaGenerator:
        def __init__(self, document_category: str):
            self.document_category = document_category
            self.schema_path = DocumentMapper.get_path_for_document_schema_by_name(name=document_category)
            
            self.schema = self.__load_schema()
            self.logger = get_logger(self.__class__.__name__)
            self.knowledge_base_wrapper = get_knowledge_base_wrapper()
            
        def __count_groups(self) -> int:
            return len(self.schema)
        
        def __count_total_fields_to_fill(self) -> int:
            fields_count = 0
            for gr in self.schema:
                fields_count += len(gr["fields"])
            return fields_count
        
        async def fill_schema(self, company_id: str, project_id: str) -> SchemaProjectSchema:
            # TODO: Add check if any nodes containing useful data exist
            from pathlib import Path
            schema_file_name = Path(self.schema_path).name
            self.logger.info(f"Filling schema template {schema_file_name}...")
            
            groups_count = self.__count_groups()
            groups = []
            for g_idx, gr in enumerate(self.schema):
                group = SchemaProjectGroup(
                    group_id = gr["group_id"],
                    group_name = gr["group_name"],
                    fields = []
                )
                fields_count = len(gr["fields"])
                for f_idx, fd in enumerate(gr["fields"]):
                    field_value = await self.knowledge_base_wrapper.query(company_id=company_id, project_id=project_id, question=fd["prompt"])
                    field = SchemaGroupField(
                        key = fd["key"],
                        type = fd["type"],
                        required = fd["required"],
                        prompt = fd["prompt"],
                        value = field_value
                    )
                    group.fields.append(field)
                    self.logger.info(f"Filled {f_idx + 1} / {fields_count} fields of group {g_idx + 1}.")
                self.logger.info(f"Filled {g_idx + 1} / {groups_count} groups.")
                groups.append(group)
            
            project_schema = SchemaProjectSchema(
                company_id=company_id,
                project_id=project_id,
                schema_type_name=self.schema_type.get_key(),
                date_created=datetime.datetime.now().isoformat(),
                groups=groups
            )
            return project_schema

        @staticmethod        
        def save_filled_schema_to_file(filled_schema: SchemaProjectSchema) -> str:
            import tempfile
            
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                tmp_file.write(filled_schema.model_dump_json().encode("utf-8"))
                tmp_file_path = tmp_file.name
            return tmp_file_path
        
        def __load_schema(self):
            path = DocumentMapper.get_path_for_document_schema_by_name(name=self.document_category)
            import json
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        
    
    @staticmethod
    async def fill_schema(document_category: str, company_id: str, project_id: str):
        schema_generator = DocumentGenerator.SchemaGenerator(
            document_category=document_category
        )
        
        return await schema_generator.fill_schema(
            company_id=company_id,
            project_id=project_id
        )
        
    @staticmethod
    def save_filled_schema_to_file(filled_schema: SchemaProjectSchema) -> str:
        return DocumentGenerator.SchemaGenerator.save_filled_schema_to_file(filled_schema=filled_schema)
    
    @staticmethod
    async def generate_schema_document(document_category: str, company_id: str, project_id: str) -> str:
        schema_generator = DocumentGenerator.SchemaGenerator(
            document_category=document_category
        )
        
        filled_schema = await schema_generator.fill_schema(
            company_id=company_id,
            project_id=project_id
        )
        
        file_path = DocumentGenerator.save_filled_schema_to_file(filled_schema=filled_schema)
        return file_path