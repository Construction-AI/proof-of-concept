from functools import lru_cache

from app.infra.instances_qdrant import get_qdrant_aclient, get_qdrant_client
from app.core.config import get_settings
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core.storage import StorageContext
from llama_index.core import VectorStoreIndex, Document
from llama_index.core.readers import SimpleDirectoryReader
from llama_index.readers.file import PyMuPDFReader
from llama_index.core.vector_stores import MetadataFilters, ExactMatchFilter
from llama_index.core.schema import BaseNode

from llama_index.core.retrievers import QueryFusionRetriever
from llama_index.retrievers.bm25 import BM25Retriever
from llama_index.postprocessor.sbert_rerank import SentenceTransformerRerank
from llama_index.core.query_engine import RetrieverQueryEngine

from app.models.files import KBFile

from llama_index.core.node_parser import SentenceWindowNodeParser
from llama_index.core.postprocessor import MetadataReplacementPostProcessor
from llama_index.core.schema import NodeWithScore

from app.core.logger import get_logger
from typing import Optional, List

SENTENCE_WINDOW_PARSER = SentenceWindowNodeParser.from_defaults(window_size=3)
WINDOW_POST = MetadataReplacementPostProcessor(target_metadata_key="window")

class KnowledgeBaseWrapper:
    def __init__(self):
        self.async_client = get_qdrant_aclient()
        self.client = get_qdrant_client()
        self.base_settings = get_settings()
        self.vector_store = QdrantVectorStore(
            collection_name=self.base_settings.QDRANT_COLLECTION,
            client=self.client,
            aclient=self.async_client,
        )
        self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
        
        self.index = VectorStoreIndex.from_vector_store(
            vector_store=self.vector_store,
        )
                
        self.reranker = SentenceTransformerRerank(
            model="cross-encoder/ms-marco-MiniLM-L-6-v2",
            top_n=6,
        )
                
        self.logger = get_logger("KnowledgeBase")
        
    async def __check_create_default_collection(self) -> None:
        if not (await self.__check_default_collection_exists()):
            self.logger.info(f"Default collection `{self.base_settings.QDRANT_COLLECTION}` does not exist. Creating...")
            await self.__create_default_collection()
            self.logger.info(f"Default collection created.")
            
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
        # Adds a new document to the knowledge base after performing necessary checks.
        await self.__check_create_default_collection()
            
        if await self.check_nodes_exist(file=file):
            raise Exception("Nodes already exist for given `file_id`. Did you mean to use `upsert_document`?")
        
        docs = self.__load_documents(file=file)
        if not docs:
            raise ValueError(f"No docs extracted from file: {file.local_path}")
        
        nodes = await SENTENCE_WINDOW_PARSER.aget_nodes_from_documents(documents=docs)
        await self.index.ainsert_nodes(nodes)
        self.logger.info(f"Document {file.file_id} has been added to the knowledge base. Nodes count: {len(nodes)}.")
        
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
        await self.__check_create_default_collection()
        
        # Query the knowledge base with metadata filters and return the response
        filters = MetadataFilters(
            filters=[
                ExactMatchFilter(key="company_id", value=company_id),
                ExactMatchFilter(key="project_id", value=project_id)
            ]
        )
        
        if document_type:
            filters.filters.append(ExactMatchFilter(key="document_type", value=document_type))
        if document_category:
            filters.filters.append(ExactMatchFilter(key="document_category", value=document_category))
        if file_name:
            filters.filters.append(ExactMatchFilter(key="file_name", value=file_name))

        retriever = self.index.as_retriever(
            similarity_top_k=10,
            filters=filters
        )
        
        # 3. Create a FRESH Fusion Retriever
        query_engine = RetrieverQueryEngine.from_args(
            retriever=retriever,
            response_mode="compact",
            node_postprocessors=[self.reranker]
        )

        response = await query_engine.aquery(question)
        return response.response
    
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
        await self.__check_create_default_collection()
        
        nodes = await self.__get_nodes_for_document(
            company_id=company_id,
            project_id=project_id,
            document_category=document_category,
            document_type=document_type
        )
        if len(nodes) == 0:
            self.logger.info("No nodes matching given parameters were found. Nothing to delete.")
            return
        node_ids = [node.node_id for node in nodes]
        await self.index.vector_store.adelete_nodes(node_ids=node_ids)
        file_path = self.__construct_file_id_from_data(
            company_id,
            project_id,
            document_category,
            document_type
        )
        self.logger.info(f"Deleted nodes with path: {file_path}.")
        
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
        await self.__check_create_default_collection()
        
        # Deletes existing document and adds the new one to ensure up-to-date content.
        await self.delete_document(
            company_id=file.company_id,
            project_id=file.project_id,
            document_category=file.document_category,
            document_type=file.document_type
       )
        await self.upload_document(file=file)
        
    def __load_documents(self, file: KBFile) -> list[Document]:
        reader = SimpleDirectoryReader(
            input_files=[file.local_path],
            filename_as_id=False,
            file_extractor={".pdf": PyMuPDFReader()}
        )
        
        docs = reader.load_data()
        for d in docs:
            d.metadata.setdefault("page_label", d.metadata.get("source", None))
            d.metadata.setdefault("company_id", file.company_id)
            d.metadata.setdefault("project_id", file.project_id)
            d.metadata.setdefault("document_category", file.document_category)
            d.metadata.setdefault("document_type", file.document_type)
            d.metadata.setdefault("file_name", file.file_name)
            d.metadata.setdefault("file_id", file.file_id)
            d.metadata.setdefault("doc_id", file.file_id)
        return docs
        
    async def __get_nodes_for_document(self, company_id: str, project_id: str, document_category: str, document_type: Optional[str] = None, file_name: Optional[str] = None) -> list[BaseNode]:
        await self.__check_create_default_collection()
        
        filters = MetadataFilters(
                filters=[
                    ExactMatchFilter(key="company_id", value=company_id),
                    ExactMatchFilter(key="project_id", value=project_id),
                    ExactMatchFilter(key="document_category", value=document_category)
                ]
        )
        
        if document_type:
            filters.filters.append(ExactMatchFilter(key="document_type", value=document_type))
        if file_name:
            filters.filters.append(ExactMatchFilter(key="file_name", value=file_name))
            
        nodes = await self.index.vector_store.aget_nodes(filters=filters)
        return nodes
    
    async def check_nodes_exist(self, file: KBFile) -> bool:
        await self.__check_create_default_collection()
        nodes = await self.__get_nodes_for_document(
                                                    company_id=file.company_id,
                                                    project_id=file.project_id,
                                                    document_category=file.document_category,
                                                    document_type=file.document_type,
                                                    file_name=file.file_name
                                                    )
        return len(nodes) > 0

    async def __check_default_collection_exists(self) -> bool:
        return await self.async_client.collection_exists(collection_name=self.base_settings.QDRANT_COLLECTION)
    
    async def __create_default_collection(self):
        await self.async_client.create_collection(
                collection_name=self.base_settings.QDRANT_COLLECTION,
                vectors_config={"size": self.base_settings.EMBEDDING_DIMENSION, "distance": "Cosine"}
            )
        
    def __construct_file_id_from_data(self, company_id: str, project_id: str, document_category: str, document_type: str, file_name: Optional[str] = None) -> str:
        if file_name:
            return f"{company_id}/{project_id}/{document_category}/{document_type}/{file_name}"
        return f"{company_id}/{project_id}/{document_category}/{document_type}/*"
            
    
@lru_cache()
def get_knowledge_base_wrapper() -> KnowledgeBaseWrapper:
    return KnowledgeBaseWrapper()