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
        
    async def generate_docx(self, document_category: str, company_id: str, project_id: str) -> LocalFile:
        from app.models.document import SchemaDocument, DocumentType, DocumentMapper
        document_type = DocumentType(type=document_category)
        file = FSFile(
            company_id=company_id,
            project_id=project_id,
            document_category=document_type.type,
            document_type="filled_schema"
        )
        target_file, temp_path = self.read_document(file=file)
        import json
        from docxtpl import DocxTemplate
        
        with open(temp_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            document = SchemaDocument.from_data(data=data)
            clean_json = document.clean_json
            template = DocxTemplate(DocumentMapper.get_path_for_document_template_by_name(name=document_category))
            template.render(context=clean_json)
            docx_file_name = "generated_" + document_category + ".docx"
            docx_path = f"/tmp/{docx_file_name}"
            template.save(docx_path)
            saved_file = LocalFile(
                company_id=company_id,
                project_id=project_id,
                document_category=document_category,
                local_path=docx_path,
                document_subtype="docx"
            )
            self.file_storage_wrapper.upsert_file(target_file=saved_file)
            return saved_file
        return None
    