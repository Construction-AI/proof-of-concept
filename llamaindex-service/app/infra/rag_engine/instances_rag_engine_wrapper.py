from functools import lru_cache

from app.infra.file_storage.instances_file_storage_wrapper import get_file_storage_wrapper
from app.infra.knowledge_base.instances_knowledge_base import get_knowledge_base_wrapper
from app.infra.document_generator.instances_document_generator import DocumentGenerator
from app.infra.instances_llamaindex import get_llamaindex_contexts
from app.core.logger import get_logger

from llama_index.core.storage import StorageContext
from app.models.files import FSFile, LocalFile, KBFile
from typing import Optional

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
        
        # 3. Generate and fill schema file
        # TODO: Change from hard-coded to real values from request
        from pathlib import Path
        schema_type = SchemaType.OPIS_KONSTRUKCJI
        file_path = await DocumentGenerator.generate_schema_document(schema_type=schema_type, company_id=file.company_id, project_id=file.project_id)
        if file_path:
            file_name = "filled" + Path(schema_type.get_path()).name
            schema_file: LocalFile = file
            schema_file.document_type = "schema"
            schema_file.local_path = file_path
            schema_file.forced_file_name = file_name
            self.file_storage_wrapper.upload_file(local_file=schema_file)
            self.logger.info(f"Schema file has been generated and uploaded to FS: {schema_file.remote_file_path}.")
        
    async def upsert_document(self, file: LocalFile):
        # 1. Upsert to file storage
        self.file_storage_wrapper.upsert_file(old_file=file, new_file=file)
        
        # 2. Upsert to knowledge base
        await self.knowledge_base_wrapper.upsert_document(file=KBFile.fromLocalFile(file=file))
        
        # 3. Generate and fill schema file
        # TODO: Change from hard-coded to real values from request
        from pathlib import Path
        schema_type = SchemaType.OPIS_KONSTRUKCJI
        file_path = await DocumentGenerator.generate_schema_document(schema_type=schema_type, company_id=file.company_id, project_id=file.project_id)
        if file_path:
            file_name = "filled_" + Path(schema_type.get_path()).name
            schema_file: LocalFile = file
            schema_file.document_type = "schema"
            schema_file.local_path = file_path
            schema_file.forced_file_name = file_name
            self.file_storage_wrapper.upsert_file(old_file=schema_file, new_file=schema_file)
            self.logger.info(f"Schema file has been generated and uploaded to FS: {schema_file.remote_file_path}.")
                
        self.logger.info(f"Document {file.file_id} has been upserted.")
        
    def read_document(self, file: FSFile) -> str:
        temp_path = self.file_storage_wrapper.read_file(target_file=file)
        return temp_path
    
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
        
        
        
@lru_cache()
def get_rag_engine_wrapper():
    return RagEngineWrapper()