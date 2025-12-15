from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
from app.core.logger import get_logger
from app.infra.knowledge_base.instances_knowledge_base import get_knowledge_base_wrapper
from app.infra.file_storage.instances_file_storage_wrapper import get_file_storage_wrapper
from app.infra.document_generator.instances_document_generator import DocumentGenerator, DocumentMapper
from app.models.files import LocalFile, FSFile
from app.models.document_state import DocumentType

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
        if not self.is_loaded:
            raise Exception("Document is not loaded. Use `document.load()` first.")
        system_prompt = self.meta.system_instruction
        for path, prompt_text, field_obj in self.__extract_prompts(self.data):
            user_prompt = f"""
            Zadanie: {prompt_text}
            Przykładowe odpowiedzi: {field_obj["example"]}
            """
            field_obj['value'] = await self.knowledge_base.fill_a_field(
                company_id=self.meta.company_id, project_id=self.meta.project_id,
                system_prompt=system_prompt, user_prompt=user_prompt
                )
        self.is_filled = True
        
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
    def clean_json(self) -> None:
        if not self.is_filled:
            raise Exception()
        
        if not self.data:
            raise Exception("No field schema provided for document.")
        data = {}
        for path, prompt_text, field_obj in self.__extract_prompts(self.data):
            data[path] = field_obj["value"]
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


# class Document(ABC):
#     def __init__(self, schema_path: str, version_id: int, date_created: datetime, last_modified: datetime, author: str, company_id: str, project_id: str, data: dict):
#         assert schema_path or data, "Either `schema_path` or `data` is required."
#         self.schema_path = schema_path
#         self.version_id = version_id
#         self.date_created = date_created
#         self.last_modified = last_modified
#         self.author = author
#         self.company_id = company_id
#         self.project_id = project_id
#         self.data = data
        
#         self.knowledge_base = get_knowledge_base_wrapper()
#         self.file_storage = get_file_storage_wrapper()
#         self.logger = get_logger(self.__class__.__name__)
        
#     @property
#     def is_loaded(self) -> bool:
#         return self.data is not None
    
#     @property
#     def meta(self) -> dict:
#         if not self.is_loaded:
#             raise Exception("You need to use `document.load()` before accessing meta.")
#         return self.data["meta"]
    
#     @property
#     def is_filled(self) -> bool:
#         return self.meta["date_created"] is not None
    
#     def get_path(self) -> str:
#         return self.schema_path
    
#     def load(self) -> None:
#         import json
#         with open(self.schema_path, "r", encoding="utf-8") as f:
#             self.data = json.load(f)
        
#     async def fill(self) -> None:
#         if not self.is_loaded:
#             raise Exception("Document is not loaded. Use `document.load()` first.")
#         self.__set_metadata(data=self.data)
#         system_prompt = self.meta["system_instruction"]
#         for path, prompt_text, field_obj in self.__extract_prompts(self.data):
#             user_prompt = f"""
#             Zadanie: {prompt_text}
#             Przykładowe odpowiedzi: {field_obj["example"]}
#             """
#             field_obj['value'] = await self.knowledge_base.fill_a_field(
#                 company_id=self.company_id, project_id=self.project_id,
#                 system_prompt=system_prompt, user_prompt=user_prompt
#                 )
#         return None
    
    
#     async def generate(self) -> LocalFile:
#         if not self.is_filled:
#             raise Exception("Document is not filled. Use `document.fill()` first.")
#         file_path = self.__save_filled_schema_to_file(filled_schema=self.data)
#         file_name = "filled_" + self.get_doc_type() + ".json"
#         file = LocalFile(
#             company_id=self.company_id,
#             project_id=self.project_id,
#             document_category=self.get_doc_type(),
#             local_path=file_path,
#             document_subtype="filled_schema",
#             forced_file_name=file_name
#         )
#         self.file_storage.upsert_file(target_file=file)
#         return file
    
#     def __set_metadata(self, data: dict) -> None:
#         now = datetime.now().isoformat()
#         data["meta"]["company_id"] = self.company_id
#         data["meta"]["project_id"] = self.project_id
#         data["meta"]["author"] = self.author
#         data["meta"]["date_created"] = now
#         data["meta"]["date_modified"] = now
#         data["meta"]["document_category"] = self.get_doc_type()
        
#     def __save_filled_schema_to_file(self, filled_schema: dict) -> str:
#         import tempfile
#         import json
#         with tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8') as tmp_file:
#             json.dump(filled_schema, tmp_file, ensure_ascii=False)
#             tmp_file_path = tmp_file.name
#         return tmp_file_path
    
#     def __extract_prompts(self, data, path=""):
#         if isinstance(data, dict):
#             if "prompt" in data and "value" in data:
#                 yield path, data["prompt"], data
#             else:
#                 for key, value in data.items():
#                     new_path = f"{path}.{key}" if path else key
#                     yield from self.__extract_prompts(value, new_path)
#         elif isinstance(data, list):
#             for index, item in enumerate(data):
#                 new_path = f"{path}[{index}]"
#                 yield from self.__extract_prompts(item, new_path)
    
#     def flatten(self) -> list[dict]:
#         if not self.data:
#             raise Exception("Document has no filled schema.")
#         filled_schema = self.data
#         result = []
#         for path, prompt_text, field_obj in self.__extract_prompts(filled_schema):
#             result.append({
#                 "path": path,
#                 "value": field_obj["value"]
#             })
#         return result
                        
#     def get_clean_json_for_render(self):
#         if not self.data:
#             raise Exception("No field schema provided for document.")
#         data = {}
#         for path, prompt_text, field_obj in self.__extract_prompts(self.data):
#             data[path] = field_obj["value"]
#         return self.__restore_tree_structure(data=data)
    
#     def __restore_tree_structure(self, data: dict) -> dict:
#         result = {}
#         for key, value in data.items():
#             parts = key.split('.')
#             d = result
#             for part in parts[:-1]:
#                 if part not in d:
#                     d[part] = {}
#                 d = d[part]
#             d[parts[-1]] = value
#         return result
    
#     @staticmethod
#     @abstractmethod
#     def fromFilledSchema(filled_schema: dict):
#         pass
        
#     @staticmethod
#     @abstractmethod
#     def get_valid_doc_types() -> list[str]:
#         pass
    
#     @staticmethod
#     @abstractmethod
#     def get_doc_type() -> str:
#         pass
    
#     @staticmethod
#     @abstractmethod
#     def get_template_path() -> str:
#         pass
    
#     @staticmethod
#     def create_document(document_category: str, company_id: str, project_id: str, author: Optional[str] = "unknown"):
#         if document_category in HSEDocument.get_valid_doc_types():
#             return HSEDocument(author=author, company_id=company_id, project_id=project_id)
#         raise ValueError(f"Document category not recognized: {document_category}.")
        
    
# class HSEDocument(Document):    
#     def __init__(self, company_id: str, project_id: str, author: Optional[str] = "unknown", version_id: Optional[int] = 0, date_created: Optional[datetime] = datetime.now(), last_modified: Optional[datetime] = datetime.now(), filled_schema: Optional[dict] = None):
#         Document.__init__(self, DocumentMapper.get_path_for_document_schema_by_name(DocumentMapper.__HSE_KEY), version_id, date_created, last_modified, author, company_id, project_id, filled_schema)

#     @staticmethod
#     def get_valid_doc_types():
#         return ["bioz", "health_and_safety_plan"]
    
#     @staticmethod
#     def get_doc_type() -> str:
#         return HSEDocument.DOC_TYPE
    
#     @staticmethod
#     def get_template_path() -> str:
#         return HSEDocument.DOCX_TEMPLATE
    
#     @staticmethod
#     def fromFilledSchema(filled_schema: dict):
#         meta = filled_schema["meta"]
#         return HSEDocument(
#             date_created=meta["date_created"],
#             last_modified=meta["date_modified"],
#             author=meta["author"],
#             company_id=meta["company_id"],
#             project_id=meta["project_id"],
#             filled_schema=filled_schema
#         )
        