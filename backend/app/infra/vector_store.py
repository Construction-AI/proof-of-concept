from qdrant_client import QdrantClient, AsyncQdrantClient
from qdrant_client.conversions import common_types as q_types
from app.core.config import settings
from app.core.logger import get_logger

from app.infra.document_identifier import DocumentIdentifier

from fastapi import UploadFile


from llama_index.core.llms import ChatMessage, MessageRole

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

from llama_index.core import PromptTemplate

import shutil
from app.modules.rag.schemas import AnswerWithConfidence
from typing import Optional, Type, Any, List, Dict

from pydantic import BaseModel, create_model, Field


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

        # reranker setup to give nodes in proper order
        self.reranker = SentenceTransformerRerank(
            model=settings.QDRANT_RERANKER_MODEL,
            top_n=settings.QDRANT_RERANKER_TOP_N,
            device=settings.REREANKER_DEVICE
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
                    distance="Cosine" # type: ignore
                ))
            self.logger.info(f"Default collection ({self.collection_name}) has been created")
        except Exception as e:
            self.logger.error(f"Failed to create default collection: {str(e)}")
            self.initialized = False
        
    async def upload_document(self, file: UploadFile, identifier: DocumentIdentifier):
        if await self._nodes_exist_for_storage_key(storage_key=identifier.storage_key):
            raise Exception(f"Nodes already exist for `storage_key` ({identifier.storage_key})")
        
        docs = self._load_documents(file=file, identifier=identifier)
        if not docs:
            raise Exception(f"No docs were extracted from file: {file.filename}")
        
        nodes = await SENTENCE_WINDOW_PARSER.aget_nodes_from_documents(documents=docs)
        await self.index.ainsert_nodes(nodes)
        self.logger.info(f"Document {file.filename} has been added to the knowledge base. Nodes count: {len(nodes)}.")
        
    async def delete_document(self, identifier: DocumentIdentifier):
        nodes: list[BaseNode] = await self._get_nodes_for_storage_key(storage_key=identifier.storage_key)
        if len(nodes) == 0:
            self.logger.info("No nodes matching given storage key. Skipping delete.")
            return
        node_ids = [node.node_id for node in nodes]
        await self.index.vector_store.adelete_nodes(node_ids=node_ids)
        self.logger.info(f"Deleted nodes of `storage_key`: {identifier.storage_key}")
        
    async def query(self, question: str, storage_keys: list[str]) -> str:
        query_engine = self._build_query_engine( # type: ignore
            storage_keys=storage_keys
        )
        response = await query_engine.aquery(question)
        return response.response
    
    async def chat_with_history(self, question: str, history: List[Dict[str, str]], storage_keys: List[str], system_prompt: str) -> str:
        chat_history: List[str] = []
        for msg in history:
            role = MessageRole.USER if msg["role"] == "user" else MessageRole.ASSISTANT
            chat_history.append(ChatMessage(role=role, content=msg["content"]))
            
        # 2. Konfiguracja retrievera (jak w zwykłym zapytaniu)
        filters = MetadataFilters(
            filters=[MetadataFilter(key="storage_key", operator="in", value=storage_keys)]
        )
        retriever = self.index.as_retriever(similarity_top_k=10, filters=filters)
        
        # 3. Inicjalizacja silnika czatu 
        chat_engine = self.index.as_chat_engine( # type: ignore
            chat_history=chat_history,
            system_prompt=system_prompt,
            retriever=retriever,
            node_postprocessors=[WINDOW_POST, self.reranker]
        )
        
        # 4. Asynchroniczne odpytanie
        response = await chat_engine.achat(question)
        return response.response
    
    async def query_with_confidence(self, question: str, storage_keys: list[str]) -> dict[str, Any]:
        query_engine: RetrieverQueryEngine = self._build_query_engine(storage_keys=storage_keys, output_cls=AnswerWithConfidence, response_mode="tree_summarize") # type: ignore

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
    
    def _build_query_engine(self, storage_keys: list[str], output_cls: Optional[Type] = None, response_mode: Optional[str] = None, text_qa_template: Optional[PromptTemplate] = None) -> RetrieverQueryEngine: # type: ignore
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
            
        if text_qa_template:
            args["text_qa_template"] = text_qa_template
        
        
        query_engine: RetrieverQueryEngine = RetrieverQueryEngine.from_args(**args) # type: ignore
        return query_engine
        
        
    def _load_documents(self, file: UploadFile, identifier: DocumentIdentifier) -> list[Document]:
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
        
    async def _nodes_exist_for_storage_key(self, storage_key: str) -> bool:
        return len(await self._get_nodes_for_storage_key(storage_key=storage_key)) > 0
            
    async def _get_nodes_for_storage_key(self, storage_key: str) -> list[BaseNode]:
        filters = MetadataFilters(
            filters=[
                ExactMatchFilter(key="storage_key", value=storage_key)
            ]
        )
        
        nodes = await self.index.vector_store.aget_nodes(filters=filters)
        return nodes

    def _create_dynamic_schema(self, expected_type: Type[Any]) -> Type[BaseModel]:
        # Wykrywamy, czy Pydantic oczekuje od nas listy
        is_list = getattr(expected_type, '__origin__', expected_type) is list
        
        # Dynamiczny opis w zależności od typu - wymusza na LLM poprawne strukturyzowanie JSONa
        answer_desc = (
            "A list of separate points. EACH point/element must be a separate string in the array. "
            "DO NOT put multiple points into a single string."
        ) if is_list else (
            "The factual answer to the instruction, strictly matching the requested format / type"
        )

        return create_model(
            "DynamicResponse",
            answer=(expected_type, Field(..., description=answer_desc)),
            confidence_score=(float, Field(..., description="A score from 0.0 to 1.0 indicating how confident you are that the context fully answers the question.")),
            reasoning=(str, Field(..., description="Explanation of why this answer and confidence score were given."))
        )
    
    async def query_with_dynamic_type(
            self,
            instruction: str,
            output_type: Type[Any],
            storage_keys: List[str]
    ) -> Dict[str, Any]:
        DynamicSchema = self._create_dynamic_schema(expected_type=output_type)
        
        # Sprawdzamy, czy oczekujemy listy w tym węźle AST
        is_list = getattr(output_type, '__origin__', output_type) is list
        
        # Dynamiczne reguły wstrzykiwane prosto do promptu
        format_rules = ""
        if is_list:
            format_rules = (
                "- UWAGA FORMATOWANIE: Zwracasz LISTĘ (array). "
                "Każdy zidentyfikowany punkt/zagrożenie musi być OSOBNYM elementem tablicy! "
                "Nie wrzucaj całego tekstu do jednego stringa. "
                "Nie używaj ręcznej numeracji (np. '1.', '2.') na początku stringów."
            )
        else:
            format_rules = "- Odpowiedz w formie ciągłego, spójnego tekstu (string)."

        QA_PROMPT_TMPL = (
            "Jesteś naczelnym inżynierem budownictwa i ekspertem ds. BHP. "
            "Twoim zadaniem jest pisanie BARDZO SZCZEGÓŁOWYCH, wyczerpujących i profesjonalnych raportów.\n\n"
            "Zasady:\n"
            "- Nigdy nie odpowiadaj pojedynczymi zdaniami. Każdy punkt analizuj dogłębnie.\n"
            "- Opisuj przyczyny, przewidywane skutki i wymagane działania naprawcze/zapobiegawcze.\n"
            "- Jeśli w bazie wiedzy nie znajdziesz odpowiedzi, to zwróć NULL albo None.\n"
            "- Używaj specjalistycznego słownictwa z branży budowlanej.\n"
            f"{format_rules}\n\n"  # <--- Wstrzykujemy dynamiczne reguły formatowania
            "Informacje kontekstowe z bazy wiedzy:\n"
            "---------------------\n"
            "{context_str}\n"
            "---------------------\n"
            "Polecenie: {query_str}\n"
            "Wyczerpująca odpowiedź:"
        )
        
        qa_prompt = PromptTemplate(QA_PROMPT_TMPL)

        query_engine: RetrieverQueryEngine = self._build_query_engine( # type: ignore
            storage_keys=storage_keys,
            output_cls=DynamicSchema,
            response_mode="tree_summarize",
            text_qa_template=qa_prompt
        )

        response = await query_engine.aquery(instruction)
        structured_data = response.response

        source_list: list[Dict[str, Any]] = []
        for node in response.source_nodes:
            meta = node.node.metadata
            source_name = f'file: [{meta.get("file_name", "Unknown File")}], page: [{meta.get("page_label", "Unknown Page")}]'
            score = f"{node.score:.2f}" if node.score else "N/A"

            original_sentence = meta.get("original_text", "Sentence not found")
            context_window = meta.get("window", "Context not found")

            source_list.append({
                "source": source_name,
                "node_confidence": score,
                "exact_sentence": original_sentence,
                "context_window": context_window
            })

        return {
            "answer": structured_data.answer, 
            "llm_confidence": structured_data.confidence_score,
            "reasoning": structured_data.reasoning,
            "sources": source_list
        }
    
vector_store_client = VectorStoreClient()