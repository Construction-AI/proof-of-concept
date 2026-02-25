from sqlalchemy.orm import Session
from app.core.logger import get_logger

from app.modules.documents.models import Document
from app.modules.documents.service import DocumentService

from app.modules.projects.models import Project
from app.modules.projects.service import ProjectService

from app.infra.vector_store import vector_store_client

from typing import Any, Type

class RagService:
    LOGGER = get_logger("RagService")
    
    @staticmethod
    async def query_documents(db: Session, question: str, document_ids: list[int], user_id: int) -> str:
        docs: list[Document] = DocumentService.get_documents_by_ids(db=db, document_ids=document_ids)
        docs = list(filter(lambda doc: doc.owner_id == user_id, docs))
        storage_keys: list[str] = [doc.storage_key for doc in docs]
        return await vector_store_client.query(question=question, storage_keys=storage_keys)
    
    @staticmethod
    async def query_project(db: Session, question: str, project_id: int, user_id: int) -> str:
        project: Project = ProjectService.get_project_by_id(db=db, project_id=project_id)
        if not project or project.owner_id != user_id:
            raise Exception(f"Project `{project_id}` does not exist or belongs to different user.")

        docs: list[Document] = DocumentService.get_documents_by_project_id(db=db, project_id=project_id, user_id=user_id)
        doc_ids = [doc.id for doc in docs]
        return await RagService.query_documents(db=db, question=question, document_ids=doc_ids, user_id=user_id)
    
    @staticmethod
    async def query_with_confidence(db: Session, question: str, project_id: int, user_id: int):        
        project: Project = ProjectService.get_project_by_id(db=db, project_id=project_id)
        if not project or project.owner_id != user_id:
            raise Exception(f"Project `{project_id}` does not exist or belongs to different user.")

        docs: list[Document] = DocumentService.get_documents_by_project_id(db=db, project_id=project_id, user_id=user_id)
        storage_keys: list[str] = [doc.storage_key for doc in docs]
        details: dict[str, Any] = await vector_store_client.query_with_confidence(question=question, storage_keys=storage_keys)
        return details
    
    @staticmethod
    async def query_with_dynamic_type(db: Session, instruction: str, output_type: Type[Any], project_id: int, user_id: int):
        docs: list[Document] = DocumentService.get_documents_by_project_id(db=db, project_id=project_id, user_id=user_id)
        storage_keys: list[str] = [doc.storage_key for doc in docs]
        return await vector_store_client.query_with_dynamic_type(instruction=instruction, output_type=output_type, storage_keys=storage_keys)
    
    @staticmethod
    async def chat_with_history(question: str, history: list[dict[str, str]], storage_keys: list[str], system_prompt: str):
        return await vector_store_client.chat_with_history(question=question, history=history, storage_keys=storage_keys, system_prompt=system_prompt)


        