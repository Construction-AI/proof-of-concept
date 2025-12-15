from functools import lru_cache

from app.models.files import FSFile, LocalFile, KBFile
from typing import Optional, Tuple

from app.api.services.rag_engine_service import RagEngineService

class RagEngineWrapper:
    def __init__(self):
        self.rag_engine_service = RagEngineService()
        
    async def upload_document(self, file: LocalFile):
        await self.rag_engine_service.upload_document(file=file)
                
    async def upsert_document(self, file: LocalFile):
        await self.rag_engine_service.upsert_document(file=file)
        
    def read_document(self, file: FSFile) -> Tuple[FSFile, str]:
        return self.rag_engine_service.read_document(file=file)
    
    async def query(self, question: str, company_id: str, project_id: str, document_type: Optional[str] = None, document_category: Optional[str] = None, file_name: Optional[str] = None, k: int = 5) -> str:
        return await self.rag_engine_service.query(
            question=question,
            company_id=company_id,
            project_id=project_id,
            document_type=document_type,
            document_category=document_category,
            file_name=file_name,
            k=k
        )
    
    async def delete_document(self, file: FSFile):
        await self.rag_engine_service.delete_document(file=file)
                
    async def generate_document(self, document_type: str, author: str, company_id: str, project_id: str) -> LocalFile:
        return await self.rag_engine_service.generate_document(
            document_type=document_type,
            author=author,
            company_id=company_id,
            project_id=project_id
        )
        
    async def generate_docx(self, document_category: str, company_id: str, project_id: str) -> LocalFile:
        return await self.rag_engine_service.generate_docx(
            document_category=document_category,
            company_id=company_id,
            project_id=project_id
        )
    
        
@lru_cache()
def get_rag_engine_wrapper():
    return RagEngineWrapper()