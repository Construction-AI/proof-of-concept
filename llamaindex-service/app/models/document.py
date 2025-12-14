from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
from app.core.logger import get_logger
from app.infra.knowledge_base.instances_knowledge_base import get_knowledge_base_wrapper
from app.infra.file_storage.instances_file_storage_wrapper import get_file_storage_wrapper
from app.infra.document_generator.instances_document_generator import DocumentGenerator
from app.models.files import LocalFile, FSFile

class Document(ABC):
    def __init__(self, schema_path: str, version_id: int, date_created: datetime, last_modified: datetime, author: str, company_id: str, project_id: str, data: dict):
        assert schema_path or data, "Either `schema_path` or `data` is required."
        self.schema_path = schema_path
        self.version_id = version_id
        self.date_created = date_created
        self.last_modified = last_modified
        self.author = author
        self.company_id = company_id
        self.project_id = project_id
        self.data = data
        
        self.knowledge_base = get_knowledge_base_wrapper()
        self.file_storage = get_file_storage_wrapper()
        self.logger = get_logger(self.__class__.__name__)
        
    @property
    def is_loaded(self) -> bool:
        return self.data is not None
    
    @property
    def meta(self) -> dict:
        if not self.is_loaded:
            raise Exception("You need to use `document.load()` before accessing meta.")
        return self.data["meta"]
    
    @property
    def is_filled(self) -> bool:
        return self.meta["date_created"] is not None
    
    def get_path(self) -> str:
        return self.schema_path
    
    def load(self) -> None:
        import json
        with open(self.schema_path, "r", encoding="utf-8") as f:
            self.data = json.load(f)
        
    async def fill(self) -> None:
        if not self.is_loaded:
            raise Exception("Document is not loaded. Use `document.load()` first.")
        self.__set_metadata(data=self.data)
        system_prompt = self.meta["system_instruction"]
        for path, prompt_text, field_obj in self.__extract_prompts(self.data):
            user_prompt = f"""
            Zadanie: {prompt_text}
            Przykładowe odpowiedzi: {field_obj["example"]}
            """
            field_obj['value'] = await self.knowledge_base.fill_a_field(
                company_id=self.company_id, project_id=self.project_id,
                system_prompt=system_prompt, user_prompt=user_prompt
                )
        return None
    
    async def generate(self) -> LocalFile:
        if not self.is_filled:
            raise Exception("Document is not filled. Use `document.fill()` first.")
        file_path = self.__save_filled_schema_to_file(filled_schema=self.data)
        file_name = "filled_" + self.get_doc_type() + ".json"
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
    
    def __set_metadata(self, data: dict) -> None:
        now = datetime.now().isoformat()
        data["meta"]["company_id"] = self.company_id
        data["meta"]["project_id"] = self.project_id
        data["meta"]["author"] = self.author
        data["meta"]["date_created"] = now
        data["meta"]["date_modified"] = now
        data["meta"]["document_category"] = self.get_doc_type()
        
    def __save_filled_schema_to_file(self, filled_schema: dict) -> str:
        import tempfile
        import json
        with tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8') as tmp_file:
            json.dump(filled_schema, tmp_file, ensure_ascii=False)
            tmp_file_path = tmp_file.name
        return tmp_file_path
    
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
    
    def flatten(self) -> list[dict]:
        if not self.data:
            raise Exception("Document has no filled schema.")
        filled_schema = self.data
        result = []
        for path, prompt_text, field_obj in self.__extract_prompts(filled_schema):
            result.append({
                "path": path,
                "value": field_obj["value"]
            })
        return result
                        
    def get_clean_json_for_render(self):
        if not self.data:
            raise Exception("No field schema provided for document.")
        data = {}
        for path, prompt_text, field_obj in self.__extract_prompts(self.data):
            data[path] = field_obj["value"]
        return self.__restore_tree_structure(data=data)
    
    def __restore_tree_structure(self, data: dict) -> dict:
        result = {}
        for key, value in data.items():
            parts = key.split('.')
            d = result
            for part in parts[:-1]:
                if part not in d:
                    d[part] = {}
                d = d[part]
            d[parts[-1]] = value
        return result
    
    @staticmethod
    @abstractmethod
    def fromFilledSchema(filled_schema: dict):
        pass
        
    @staticmethod
    @abstractmethod
    def get_valid_doc_types() -> list[str]:
        pass
    
    @staticmethod
    @abstractmethod
    def get_doc_type() -> str:
        pass
    
    @staticmethod
    @abstractmethod
    def get_template_path() -> str:
        pass
    
    @staticmethod
    def create_document(document_category: str, company_id: str, project_id: str, author: Optional[str] = "unknown"):
        if document_category in HSEDocument.get_valid_doc_types():
            return HSEDocument(author=author, company_id=company_id, project_id=project_id)
        raise ValueError(f"Document category not recognized: {document_category}.")
        
    
class HSEDocument(Document):
    DOC_TYPE = "health_and_safety_plan"
    DOCX_TEMPLATE = "/app/templates/szablon_bioz_paths.docx"
    
    def __init__(self, company_id: str, project_id: str, author: Optional[str] = "unknown", version_id: Optional[int] = 0, date_created: Optional[datetime] = datetime.now(), last_modified: Optional[datetime] = datetime.now(), filled_schema: Optional[dict] = None):
        from app.config.const import HSE_SCHEMA_PATH
        Document.__init__(self, HSE_SCHEMA_PATH, version_id, date_created, last_modified, author, company_id, project_id, filled_schema)

    @staticmethod
    def get_valid_doc_types():
        return ["bioz", "health_and_safety_plan"]
    
    @staticmethod
    def get_doc_type() -> str:
        return HSEDocument.DOC_TYPE
    
    @staticmethod
    def get_template_path() -> str:
        return HSEDocument.DOCX_TEMPLATE
    
    @staticmethod
    def fromFilledSchema(filled_schema: dict):
        meta = filled_schema["meta"]
        return HSEDocument(
            date_created=meta["date_created"],
            last_modified=meta["date_modified"],
            author=meta["author"],
            company_id=meta["company_id"],
            project_id=meta["project_id"],
            filled_schema=filled_schema
        )
        