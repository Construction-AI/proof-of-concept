from functools import lru_cache

from app.infra.file_storage.instances_file_storage_wrapper import get_file_storage_wrapper
from app.infra.knowledge_base.instances_knowledge_base import get_knowledge_base_wrapper
from app.infra.document_generator.instances_document_generator import DocumentGenerator
from app.infra.instances_llamaindex import get_llamaindex_contexts
from app.core.logger import get_logger

from llama_index.core.storage import StorageContext
from app.models.files import FSFile, LocalFile, KBFile
from typing import Optional, Tuple

from app.models.schema_types import SchemaType

class RagEngineWrapper:
    def __init__(self):
        self.file_storage_wrapper = get_file_storage_wrapper()
        self.knowledge_base_wrapper = get_knowledge_base_wrapper()
        
        self.llamaindex_contexts = get_llamaindex_contexts()
        self.llamaindex_storage_context: StorageContext = self.llamaindex_contexts["storage_context"]
        
        self.logger = get_logger(self.__class__.__name__)
        
    async def upload_document(self, file: LocalFile):
        # 1. Upload to file storage
        if not self.file_storage_wrapper.check_object_exists(local_file=file):
            self.file_storage_wrapper.upload_file(local_file=file)
        else:
            self.logger.info(f"Document {file.file_id} already exists in file storage. Skipping...")
        
        # 2. Upload to knowledge base
        kb_file = KBFile.fromLocalFile(file=file)
        if not await self.knowledge_base_wrapper.check_nodes_exist(file=kb_file):
            await self.knowledge_base_wrapper.upload_document(file=kb_file)
        else:
            self.logger.info(f"Document {file.file_id} already exists in knowledge base. Skipping...")
        self.logger.info(f"Document {file.file_id} has been uploaded.")
                
    async def upsert_document(self, file: LocalFile):
        # 1. Upsert to file storage
        self.file_storage_wrapper.upsert_file(target_file=file)
        
        # 2. Upsert to knowledge base
        await self.knowledge_base_wrapper.upsert_document(file=KBFile.fromLocalFile(file=file))
                
        self.logger.info(f"Document {file.file_id} has been upserted.")
        
    def read_document(self, file: FSFile) -> Tuple[FSFile, str]:
        target_file, temp_path = self.file_storage_wrapper.read_file(target_file=file)
        return target_file, temp_path 
    
    async def query(self, question: str, company_id: str, project_id: str, document_type: Optional[str] = None, document_category: Optional[str] = None, file_name: Optional[str] = None, k: int = 5) -> str:
        response = await self.knowledge_base_wrapper.query(
            question=question,
            company_id=company_id,
            project_id=project_id,
            document_type=document_type,
            document_category=document_category,
            file_name=file_name
        )
        return response
    
    async def delete_document(self, file: FSFile):
        self.file_storage_wrapper.delete_file(target_file=file)
        await self.knowledge_base_wrapper.delete_document(
            company_id=file.company_id, 
            project_id=file.project_id,
            document_category=file.document_category,
            document_type=file.document_type
        )
        
        self.logger.info(f"Document {file.file_id} has been deleted.")
                
    async def generate_document(self, doc_type: str, author: str, company_id: str, project_id: str) -> LocalFile:
        from app.models.document import HSEDocument
        document = None
        if doc_type in HSEDocument.get_valid_doc_types():
            document = HSEDocument(author=author, company_id=company_id, project_id=project_id)
            self.logger.info(f"Identified document as HSEDocument")
            return await document.generate()
        return None
        
        
        
        
@lru_cache()
def get_rag_engine_wrapper():
    return RagEngineWrapper()