from qdrant_client import QdrantClient, AsyncQdrantClient
from qdrant_client.conversions import common_types as q_types
from app.core.config import settings
from app.core.logger import get_logger

from app.infra.document_identifier import DocumentIdentifier

from fastapi import UploadFile

from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core.storage import StorageContext
from llama_index.core import VectorStoreIndex, Document
from llama_index.core.readers import SimpleDirectoryReader
from llama_index.readers.file import PyMuPDFReader
from llama_index.core.vector_stores import MetadataFilters, ExactMatchFilter, MetadataFilter
from llama_index.core.schema import BaseNode
from llama_index.postprocessor.sbert_rerank import SentenceTransformerRerank
from llama_index.core.query_engine import RetrieverQueryEngine

from llama_index.core.node_parser import SentenceWindowNodeParser
from llama_index.core.postprocessor import MetadataReplacementPostProcessor

SENTENCE_WINDOW_PARSER = SentenceWindowNodeParser.from_defaults(window_size=3)
WINDOW_POST = MetadataReplacementPostProcessor(target_metadata_key="window")

import shutil
from app.modules.rag.schemas import AnswerWithConfidence
from typing import Optional, Type, Any


class VectorStoreClient:
    def __init__(self):
        self.initialized = False
        self.collection_name = settings.BUCKET_COLLECTION_NAME
        self.logger = get_logger(self.__class__.__name__)
        
        self.__initialize_llamaindex()
        
        self.client = QdrantClient(location=settings.QDRANT_URL, timeout=30)
        self.aclient = AsyncQdrantClient(location=settings.QDRANT_URL, timeout=30)
        
        self._ensure_default_collection_exists()
        
        self.vector_store = QdrantVectorStore(
            collection_name=self.collection_name,
            client=self.client,
            aclient=self.aclient
        )
        self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
        self.index: VectorStoreIndex = VectorStoreIndex.from_vector_store(vector_store=self.vector_store) # type: ignore
        self.reranker = SentenceTransformerRerank(
            model=settings.QDRANT_RERANKER_MODEL,
            top_n=settings.QDRANT_RERANKER_TOP_N
        )
        self.initialized = True
        
    def __initialize_llamaindex(self):
        from llama_index.core.settings import Settings as LlamaSettings
        
        if settings.LLM_PROVIDER == "OPENAI":
            assert settings.LLM_PROVIDER_API_KEY is not None, "OpenAI selected as provider, `LLM_PROVIDER_API_KEY` cannot be null."

            from llama_index.llms.openai import OpenAI

            LlamaSettings.llm = OpenAI(
                model=settings.LLM_MODEL,
                api_key=settings.LLM_PROVIDER_API_KEY
            )

            from llama_index.embeddings.openai import OpenAIEmbedding
            LlamaSettings.embed_model = OpenAIEmbedding(
                    model=settings.LLM_EMBEDDING_MODEL,
                    api_key=settings.LLM_PROVIDER_API_KEY,
                    dimensions=settings.EMBEDDING_DIMENSION
                )
        else:
            assert settings.LLM_PROVIDER_BASE_URL is not None, "LMStudio selected as LLM provider, `LLM_PROVIDER_BASE_URL` cannot be null"

            from llama_index.llms.lmstudio import LMStudio
            LlamaSettings.llm = LMStudio(
                base_url=settings.LLM_PROVIDER_BASE_URL,
                model_name=settings.LLM_MODEL
            )

            from llama_index.embeddings.openai import OpenAIEmbedding
            LlamaSettings.embed_model = OpenAIEmbedding(
                    model=settings.LLM_EMBEDDING_MODEL,
                    api_key=settings.LLM_PROVIDER_API_KEY,
                    dimensions=settings.EMBEDDING_DIMENSION
                )
        
        
    def _ensure_default_collection_exists(self):
        try:
            if not self.client.collection_exists(collection_name=self.collection_name):
                self.client.create_collection(collection_name=self.collection_name, vectors_config=q_types.VectorParams(
                    size=settings.EMBEDDING_DIMENSION,
                    distance=q_types.Distance.COSINE # type: ignore
                ))
            self.logger.info(f"Default collection ({self.collection_name}) has been created")
        except Exception as e:
            self.logger.error(f"Failed to create default collection: {str(e)}")
            self.initialized = False
        
    async def upload_document(self, file: UploadFile, identifier: DocumentIdentifier):
        if await self.__nodes_exist_for_storage_key(storage_key=identifier.storage_key):
            raise Exception(f"Nodes already exist for `storage_key` ({identifier.storage_key})")
        
        docs = self.__load_documents(file=file, identifier=identifier)
        if not docs:
            raise Exception(f"No docs were extracted from file: {file.filename}")
        
        nodes = await SENTENCE_WINDOW_PARSER.aget_nodes_from_documents(documents=docs)
        await self.index.ainsert_nodes(nodes)
        self.logger.info(f"Document {file.filename} has been added to the knowledge base. Nodes count: {len(nodes)}.")
        
    async def delete_document(self, identifier: DocumentIdentifier):
        nodes: list[BaseNode] = await self.__get_nodes_for_storage_key(storage_key=identifier.storage_key)
        if len(nodes) == 0:
            self.logger.info("No nodes matching given storage key. Skipping delete.")
            return
        node_ids = [node.node_id for node in nodes]
        await self.index.vector_store.adelete_nodes(node_ids=node_ids)
        self.logger.info(f"Deleted nodes of `storage_key`: {identifier.storage_key}")
        
    async def query(self, question: str, storage_keys: list[str]) -> str:
        query_engine = self.__build_query_engine( # type: ignore
            storage_keys=storage_keys
        )
        response = await query_engine.aquery(question)
        return response.response
    
    async def query_with_confidence(self, question: str, storage_keys: list[str]) -> dict[str, Any]:
        query_engine: RetrieverQueryEngine = self.__build_query_engine(storage_keys=storage_keys, output_cls=AnswerWithConfidence, response_mode="tree_summarize") # type: ignore

        response = await query_engine.aquery(question)

        structured_output: AnswerWithConfidence = response.response

        source_list: list[str] = []
        for node in response.source_nodes:
            meta = node.node.metadata
            source_name = meta.get("source", "Unknown Source")
            score = f"{node.score:.2f}" if node.score else "N/A"
            source_list.append(f"{source_name} (Similarity: {score})")

        return {
            "answer": structured_output,
            "sources": source_list
        }
    
    def __build_query_engine(self, storage_keys: list[str], output_cls: Optional[Type] = None, response_mode: Optional[str] = None) -> RetrieverQueryEngine: # type: ignore
        filters = MetadataFilters(
            filters=[
                MetadataFilter(key="storage_key", operator="in", value=storage_keys)
            ]
        )
        retriever = self.index.as_retriever(
            similarity_top_k=10,
            filters=filters
        )

        args: dict[str, Any] = {
            "retriever": retriever,
            "node_postprocessors": [WINDOW_POST, self.reranker],
        }

        if output_cls:
            args["output_cls"] = output_cls
        if response_mode:
            args["response_mode"] = response_mode
        
        
        query_engine: RetrieverQueryEngine = RetrieverQueryEngine.from_args(**args) # type: ignore
        return query_engine
        
        
    def __load_documents(self, file: UploadFile, identifier: DocumentIdentifier) -> list[Document]:
        import os
        
        os.makedirs(name=settings.UPLOAD_DIR, exist_ok=True)
        file_path = os.path.join(settings.UPLOAD_DIR, identifier.document_name)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        reader = SimpleDirectoryReader(
            input_files=[file_path],
            filename_as_id=False,
            file_extractor={".pdf": PyMuPDFReader()}
        )
        
        docs = reader.load_data()
        for d in docs:
            d.metadata.setdefault("page_label", d.metadata.get("source", None))
            d.metadata.setdefault("project_id", identifier.project_id)
            d.metadata.setdefault("user_id", identifier.user_id)
            d.metadata.setdefault("storage_key", identifier.storage_key)
        os.remove(path=file_path)
        return docs
        
    async def __nodes_exist_for_storage_key(self, storage_key: str) -> bool:
        return len(await self.__get_nodes_for_storage_key(storage_key=storage_key)) > 0
        
    # async def check_nodes_exist(self, storage_key: str) -> bool:
    #     nodes = await self.
    
    async def __get_nodes_for_storage_key(self, storage_key: str) -> list[BaseNode]:
        filters = MetadataFilters(
            filters=[
                ExactMatchFilter(key="storage_key", value=storage_key)
            ]
        )
        
        nodes = await self.index.vector_store.aget_nodes(filters=filters)
        return nodes
    
vector_store_client = VectorStoreClient()