from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
from app.core.logger import get_logger
from app.infra.knowledge_base.instances_knowledge_base import get_knowledge_base_wrapper
from app.infra.file_storage.instances_file_storage_wrapper import get_file_storage_wrapper
from app.models.files import LocalFile
from app.models.document_state import DocumentType
from app.core.document_mapper import DocumentMapper
from app.models.field_extraction import FieldExtraction

class SchemaDocument:
    class Meta:
        def __init__(self, document_type: DocumentType, company_id: str, project_id: str, author: str, system_instruction: str, version: str, language: str, date_created: str, date_modified: str):
            self.document_type = document_type
            self.company_id = company_id
            self.project_id = project_id
            self.author = author
            self.system_instruction = system_instruction
            self.version = version
            self.language = language
            self.date_created = date_created
            self.date_modified = date_modified
                        
    def __init__(self, document_type: DocumentType, company_id: str, project_id: str, author: str, version: Optional[str] = "1.0.0", language: Optional[str] = "pl", initial_data: Optional[dict] = None):
        self.saved_path = None
        self.data = None
        
        if initial_data:
            self.data = initial_data
            self.is_filled = True
            self.__set_meta_from_data()
        else:
            self.is_filled = False
            self.schema_path = DocumentMapper.get_path_for_document_schema_by_name(name=document_type.type)
            self.load()
            self.__set_metadata(
                document_type=document_type,
                company_id=company_id,
                project_id=project_id,
                author=author,
                version=version,
                language=language,
                system_instruction=self.data["meta"]["system_instruction"]
            )
            
        # Wrappers
        self.knowledge_base = get_knowledge_base_wrapper()
        self.file_storage = get_file_storage_wrapper()
        self.logger = get_logger(self.__class__.__name__)
                
    @property
    def is_loaded(self) -> bool:
        return self.data is not None
        
    def load(self) -> None:
        if self.is_loaded:
            raise Exception("Document is already loaded.")
        
        import json
        with open(self.schema_path, "r", encoding="utf-8") as f:
            self.data = json.load(f)
            
    async def fill(self) -> None:
        try:
            if not self.is_loaded:
                raise Exception("Document is not loaded. Use `document.load()` first.")
            system_prompt = self.meta.system_instruction
            for path, prompt_text, field_obj in self.__extract_prompts(self.data):
                user_prompt = f"""
                Zadanie: {prompt_text}
                Przykładowe odpowiedzi: {field_obj["example"]}
                """
                field_extraction: FieldExtraction = await self.knowledge_base.extract_field(
                    company_id=self.meta.company_id,
                    project_id=self.meta.project_id,
                    field_prompt=user_prompt,
                    field_type=field_obj["type"]
                )
                field_obj['value'] = field_extraction.value
                field_obj['confidence'] = field_extraction.confidence
                field_obj['reasoning'] = field_extraction.reasoning
            self.data["meta"] = self.__dump_meta()
            self.is_filled = True
        except Exception as e:
            self.logger.error(str(e))
            raise e
        
    @property
    def is_saved(self) -> bool:
        return self.saved_path is not None
    
    async def save(self) -> None:
        if not self.is_filled:
            raise Exception("Document is not filled. Use `document.fill()` first.")
        
        import tempfile
        import json
        with tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8') as tmp_file:
            json.dump(self.data, tmp_file, ensure_ascii=False)
            self.saved_path = tmp_file.name
            
    def get_local_file(self) -> LocalFile:
        if not self.is_saved:
            raise Exception("Document is not saved. Use `document.save()` first.")
        file_name = "filled_" + self.meta.document_type.type + ".json"
        file = LocalFile(
            company_id=self.meta.company_id,
            project_id=self.meta.project_id,
            document_category=self.meta.document_type.type,
            local_path=self.saved_path,
            document_subtype="filled_schema",
            forced_file_name=file_name
        )
        return file
    
    @property
    def clean_json(self) -> dict:
        if not self.is_filled:
            raise Exception()
        
        if not self.data:
            raise Exception("No field schema provided for document.")
        data = {}
        for path, prompt_text, field_obj in self.__extract_prompts(self.data):
            data[path] = field_obj["value"]
        data["meta"] = self.__dump_meta()
        return self.__restore_tree_structure(data=data)
    
    # Factories
    @staticmethod
    def from_data(data: dict):
        meta = data["meta"]
        return SchemaDocument(
            document_type=meta["document_type"],
            company_id=meta["company_id"],
            project_id=meta["project_id"],
            author=meta["author"],
            version=meta["version"],
            language=meta["language"],
            initial_data=data
        )
    
    # Utils
    def __dump_meta(self) -> dict:
        return {
            "document_type": self.meta.document_type.type,
            "company_id": self.meta.company_id,
            "project_id": self.meta.project_id,
            "author": self.meta.author,
            "system_instruction": self.meta.system_instruction,
            "version": self.meta.version,
            "language": self.meta.language,
            "date_created": str(self.meta.date_created),
            "date_modified": str(self.meta.date_modified)
        }
    
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
    
    def __set_metadata(self, document_type: DocumentType, company_id: str, project_id: str, author: str, system_instruction: str, version: Optional[str] = "1.0.0", language: Optional[str] = "pl", date_created: Optional[datetime] = datetime.now(), date_modified: Optional[datetime] = datetime.now()) -> None:
        self.meta = SchemaDocument.Meta(
            document_type=document_type,
            company_id=company_id,
            project_id=project_id,
            author=author,
            system_instruction=system_instruction,
            version=version,
            language=language,
            date_created=date_created,
            date_modified=date_modified
        )
        
    def __set_meta_from_data(self) -> None:
        self.meta = SchemaDocument.Meta(
            document_type=DocumentType(type=self.data["meta"]["document_type"]),
            company_id=self.data["meta"]["company_id"],
            project_id=self.data["meta"]["project_id"],
            author=self.data["meta"]["author"],
            system_instruction=self.data["meta"]["system_instruction"],
            version=self.data["meta"]["version"],
            language=self.data["meta"]["language"],
            date_created=self.data["meta"]["date_created"],
            date_modified=self.data["meta"]["date_modified"]
        )
                    
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
