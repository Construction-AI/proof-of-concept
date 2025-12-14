from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
from app.core.logger import get_logger
from app.infra.knowledge_base.instances_knowledge_base import get_knowledge_base_wrapper
from app.infra.file_storage.instances_file_storage_wrapper import get_file_storage_wrapper
from app.infra.document_generator.instances_document_generator import DocumentGenerator
from app.models.files import LocalFile

class Document(ABC):
    def __init__(self, schema_path: str, version_id: int, date_created: datetime, last_modified: datetime, author: str, company_id: str, project_id: str):
        self.schema_path = schema_path
        self.version_id = version_id
        self.date_created = date_created
        self.last_modified = last_modified
        self.author = author
        self.company_id = company_id
        self.project_id = project_id
        
        self.knowledge_base = get_knowledge_base_wrapper()
        self.file_storage = get_file_storage_wrapper()
        self.logger = get_logger(self.__class__.__name__)
    
    def get_path(self) -> str:
        return self.schema_path
    
    def load(self):
        import json
        with open(self.schema_path, "r", encoding="utf-8") as f:
            return json.load(f)
        
    async def fill(self) -> dict:
        data = self.load()
        system_prompt = data["meta"]["system_instruction"]
        for path, prompt_text, field_obj in self.__extract_prompts(data):
            user_prompt = f"""
            Zadanie: {prompt_text}
            Przykładowe odpowiedzi: {field_obj["example"]}
            """
            field_obj['value'] = await self.knowledge_base.fill_a_field(company_id=self.company_id, project_id=self.project_id, system_prompt=system_prompt, user_prompt=user_prompt)
        return data
    
    async def generate(self) -> LocalFile:
        filled_schema = await self.fill()
        file_path = self.__save_filled_schema_to_file(filled_schema=filled_schema)
        file_name = self.get_doc_type() + ".json"
        file = LocalFile(
            company_id=self.company_id,
            project_id=self.project_id,
            document_category=self.get_doc_type(),
            local_path=file_path,
            document_type="filled_schema",
            forced_file_name=file_name
        )
        self.file_storage.upsert_file(target_file=file)
        return file
        
    def __save_filled_schema_to_file(self, filled_schema: dict) -> str:
        import tempfile
        import json
        with tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8') as tmp_file:
            json.dump(filled_schema, tmp_file, ensure_ascii=False)
            tmp_file_path = tmp_file.name
        return tmp_file_path
    
    @staticmethod
    @abstractmethod
    def get_valid_doc_types() -> list[str]:
        pass
    
    @staticmethod
    @abstractmethod
    def get_doc_type() -> str:
        pass
    
    def __extract_prompts(self, data, path=""):
        if isinstance(data, dict):
            if "prompt" in data and "value" in data:
                yield path, data["prompt"], data
            else:
                for key, value in data.items():
                    new_path = f"{path}.{key}" if path else key
                    yield from self.__extract_prompts(value, new_path)
        elif isinstance(data, list):
            for index, item in enumerate(data):
                new_path = f"{path}[{index}]"
                yield from self.__extract_prompts(item, new_path)
        
    
class HSEDocument(Document):
    DOC_TYPE = "health_and_safety_plan"
    
    def __init__(self, author: str, company_id: str, project_id: str, version_id: Optional[int] = 0, date_created: Optional[datetime] = datetime.now(), last_modified: Optional[datetime] = datetime.now()):
        from app.config.const import HSE_SCHEMA_PATH
        Document.__init__(self, HSE_SCHEMA_PATH, version_id, date_created, last_modified, author, company_id, project_id)
                    
    @staticmethod
    def get_valid_doc_types():
        return ["bioz", "health_and_safety_plan"]
    
    @staticmethod
    def get_doc_type() -> str:
        return HSEDocument.DOC_TYPE