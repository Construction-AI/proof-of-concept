from functools import lru_cache
from app.models.files import KBFile

from llama_index.core.node_parser import SentenceWindowNodeParser
from llama_index.core.postprocessor import MetadataReplacementPostProcessor
from app.models.field_extraction import FieldExtraction

from typing import Optional

SENTENCE_WINDOW_PARSER = SentenceWindowNodeParser.from_defaults(window_size=3)
WINDOW_POST = MetadataReplacementPostProcessor(target_metadata_key="window")

from app.api.services.knowledge_base_service import KnowledgeBaseService

class KnowledgeBaseWrapper:
    """
    A wrapper class for interacting with the knowledge base service, providing high-level asynchronous methods for document management and querying.
    The KnowledgeBaseWrapper class abstracts the underlying KnowledgeBaseService, offering convenient methods to upload, upsert, delete, and query documents, as well as extract specific fields from the knowledge base. It ensures proper handling of document metadata and prevents duplicate entries. This class is designed to be used in asynchronous workflows.
    Attributes:
        TOP_K (int): The default number of top similar results to retrieve in queries.
    Methods:
        - upload_document(file: KBFile):
            Asynchronously adds a document to the knowledge base, ensuring no duplicates exist for the given file.
        - query(question: str, company_id: str, project_id: str, document_type: Optional[str], document_category: Optional[str], file_name: Optional[str], k: int):
        - delete_document(company_id: str, project_id: str, document_category: str, document_type: str):
            Asynchronously deletes all nodes and associated data for a specific document identified by company, project, category, and type.
        - upsert_document(file: KBFile):
            Asynchronously upserts a document in the knowledge base by deleting any existing matching document and adding the new one.
        - extract_field(company_id: str, project_id: str, field_prompt: str, field_type: str) -> FieldExtraction:
            Asynchronously extracts a specific field from the knowledge base using a prompt and field type.
    """
    TOP_K = 6
    
    def __init__(self):
        self.knowledge_base_service = KnowledgeBaseService()
                    
    async def upload_document(self, file: KBFile):
        """
        Asynchronously adds a document to the knowledge base.
        This method checks if the default collection exists and creates it if necessary.
        It then verifies that nodes for the given file do not already exist to prevent duplicates.
        The document is loaded and parsed into nodes, which are then inserted into the index.
        Args:
            file (KBFile): The file object containing document data to be added.
        Raises:
            Exception: If nodes already exist for the given file ID.
            ValueError: If no documents are extracted from the provided file.
        Returns:
            None
        Note:
            Use `upsert_document` if you intend to update an existing document.
        """
        await self.knowledge_base_service.upload_document(file=file)
        
    async def query(self, question: str, company_id: str, project_id: str, document_type: Optional[str] = None, document_category: Optional[str] = None, file_name: Optional[str] = None, k: int = 5) -> str:
        """
        Asynchronously queries the knowledge base for relevant information based on the provided question and metadata filters.
        Args:
            question (str): The question to query against the knowledge base.
            company_id (str): The company identifier to filter documents.
            project_id (str): The project identifier to filter documents.
            document_type (Optional[str], optional): The type of document to filter (default is None).
            document_category (Optional[str], optional): The category of document to filter (default is None).
            file_name (Optional[str], optional): The file name to filter (default is None).
            k (int, optional): The number of top similar results to retrieve (default is 5).
        Returns:
            Any: The response from the query engine containing relevant information.
        Note:
            This method constructs metadata filters based on the provided arguments and queries the index asynchronously.
        """
        return await self.knowledge_base_service.query(
            question=question,
            company_id=company_id,
            project_id=project_id,
            document_type=document_type,
            document_category=document_category,
            file_name=file_name,
            k=k
        )
        
    async def delete_document(self, company_id: str, project_id: str, document_category: str, document_type: str):
        # Deletes all nodes and associated data for a specific document in the knowledge base.
        """
        Delete all nodes and associated data for a specific document identified by company, project, category, and type.

        This method retrieves all nodes matching the provided parameters and deletes them from the vector store.
        If no matching nodes are found, it logs an informational message and returns without performing any deletion.
        After deletion, it logs the file path of the deleted nodes.

        Args:
            company_id (str): The ID of the company.
            project_id (str): The ID of the project.
            document_category (str): The category of the document.
            document_type (str): The type of the document.

        Returns:
            None
        """
        await self.knowledge_base_service.delete_document(
            company_id=company_id,
            project_id=project_id,
            document_category=document_category,
            document_type=document_type
        )
        
    async def upsert_document(self, file: KBFile):
        """
        Upserts a document in the knowledge base.

        This method first deletes any existing document matching the provided file's
        company ID, project ID, document category, and document type. It then adds
        the new document to the knowledge base.

        Args:
            file (KBFile): The document file to upsert, containing metadata such as
                company_id, project_id, document_category, and document_type.

        Returns:
            None

        Note:
            This operation is asynchronous.
        """
        await self.knowledge_base_service.upsert_document(file=file)
            
    async def extract_field(self, company_id: str, project_id: str, field_prompt: str, field_type: str) -> FieldExtraction:
        return await self.knowledge_base_service.extract_field(
            company_id=company_id,
            project_id=project_id,
            field_prompt=field_prompt,
            field_type=field_type
        )
        
            
    
@lru_cache()
def get_knowledge_base_wrapper() -> KnowledgeBaseWrapper:
    return KnowledgeBaseWrapper()