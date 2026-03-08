from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Any, Type

from app.core.logger import get_logger
from app.db.session import get_db
from app.modules.documents.models import Document
from app.modules.documents.service import DocumentService
from app.modules.projects.models import Project
from app.modules.projects.service import ProjectService
from app.infra.vector_store import vector_store_client

class RagService:
    def __init__(self, db: Session):
        self.db = db
        self.logger = get_logger(self.__class__.__name__)
        
    async def query_documents(self, question: str, document_ids: list[int], user_id: int) -> str:
        document_service = DocumentService(db=self.db)
        docs: list[Document] = document_service.get_documents_by_ids(document_ids=document_ids)
        docs = list(filter(lambda doc: doc.owner_id == user_id, docs))
        storage_keys: list[str] = [doc.storage_key for doc in docs]
        return await vector_store_client.query(question=question, storage_keys=storage_keys)
    
    async def query_project(self, question: str, project_id: int, user_id: int) -> str:
        document_service = DocumentService(db=self.db)
        project_service = ProjectService(db=self.db)
        project: Project = project_service.get_project_by_id(project_id=project_id)
        if not project or project.owner_id != user_id:
            raise Exception(f"Project `{project_id}` does not exist or belongs to different user.")

        docs: list[Document] = document_service.get_documents_by_project_id(project_id=project_id, user_id=user_id)
        doc_ids = [doc.id for doc in docs]
        return await self.query_documents(question=question, document_ids=doc_ids, user_id=user_id)
    
    async def query_with_confidence(self, question: str, project_id: int, user_id: int):        
        document_service = DocumentService(db=self.db)
        project_service = ProjectService(db=self.db)
        project: Project = project_service.get_project_by_id(project_id=project_id)
        if not project or project.owner_id != user_id:
            raise Exception(f"Project `{project_id}` does not exist or belongs to different user.")

        docs: list[Document] = document_service.get_documents_by_project_id(project_id=project_id, user_id=user_id)
        storage_keys: list[str] = [doc.storage_key for doc in docs]
        details: dict[str, Any] = await vector_store_client.query_with_confidence(question=question, storage_keys=storage_keys)
        return details
    
    async def query_with_dynamic_type(self, instruction: str, output_type: Type[Any], project_id: int, user_id: int):
        document_service = DocumentService(db=self.db)
        docs: list[Document] = document_service.get_documents_by_project_id(project_id=project_id, user_id=user_id)
        storage_keys: list[str] = [doc.storage_key for doc in docs]
        return await vector_store_client.query_with_dynamic_type(instruction=instruction, output_type=output_type, storage_keys=storage_keys)
    
    async def chat_with_history(self, question: str, history: list[dict[str, str]], storage_keys: list[str], system_prompt: str):
        return await vector_store_client.chat_with_history(question=question, history=history, storage_keys=storage_keys, system_prompt=system_prompt)

def get_rag_service(db: Session = Depends(get_db)):
    return RagService(db=db)