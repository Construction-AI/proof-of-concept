from app.infra.file_storage.instances_file_storage_wrapper import get_file_storage_wrapper
from app.infra.knowledge_base.instances_knowledge_base import get_knowledge_base_wrapper
from app.infra.instances_llamaindex import get_llamaindex_contexts
from app.core.logger import get_logger

from llama_index.core.storage import StorageContext
from app.models.files import FSFile, LocalFile, KBFile
from typing import Optional, Tuple

class RagEngineService:
    def __init__(self):
        self.file_storage_wrapper = get_file_storage_wrapper()
        self.knowledge_base_wrapper = get_knowledge_base_wrapper()
        
        self.llamaindex_contexts = get_llamaindex_contexts()
        self.llamaindex_storage_context: StorageContext = self.llamaindex_contexts["storage_context"]
        
        self.logger = get_logger(self.__class__.__name__)
        
    async def upload_document(self, file: LocalFile):
        if not self.file_storage_wrapper.check_object_exists(local_file=file):
            self.file_storage_wrapper.upload_file(local_file=file)
        else:
            self.logger.info(f"Document {file.file_id} already exists in file storage. Skipping...")
        
        kb_file = KBFile.fromLocalFile(file=file)
        if not await self.knowledge_base_wrapper.check_nodes_exist(file=kb_file):
            await self.knowledge_base_wrapper.upload_document(file=kb_file)
        else:
            self.logger.info(f"Document {file.file_id} already exists in knowledge base. Skipping...")
        self.logger.info(f"Document {file.file_id} has been uploaded.")
                
    async def upsert_document(self, file: LocalFile):
        self.file_storage_wrapper.upsert_file(target_file=file)
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
                
    async def generate_document(self, document_type: str, author: str, company_id: str, project_id: str) -> LocalFile:
        from app.models.document import SchemaDocument, DocumentType
        document = SchemaDocument(document_type=DocumentType(type=document_type), author=author, company_id=company_id, project_id=project_id)
        self.logger.info(f"Identified document as {document.__class__.__name__.upper()}")
        await document.fill()
        await document.save()
        local_file = document.get_local_file()
        self.file_storage_wrapper.upsert_file(target_file=document.get_local_file())
        return local_file
        
    async def generate_docx(self, bucket: str, file_url: str) -> str:
        from app.models.schema.basic import SchemaDocument
        from app.core.schema.mapper import SchemaMapper
        import json
        from pathlib import Path
        
        file_path = self.file_storage_wrapper.read_file_from_url(bucket=bucket, file_url=file_url)
        
        with open(file_path, "r") as f:
            schema_dict = json.load(f)
            doc: SchemaDocument = SchemaMapper.parse_schema(data=schema_dict)
        from app.core.docx.generator import DocxGenerator
        gen = DocxGenerator()
        await gen.preprocess_schema(schema=doc)
        file_name = "/app/generated/generated_" + Path(file_url).name.split(".")[0] + ".docx"
        gen.generate(schema=doc, output_path=file_name)
        return file_name
    