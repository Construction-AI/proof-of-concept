from functools import lru_cache

from app.infra.clients.instances_qdrant import get_qdrant_aclient, get_qdrant_client
from app.core.settings import get_settings
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core.storage import StorageContext
from llama_index.core import VectorStoreIndex, Document
from llama_index.core.readers import SimpleDirectoryReader
from llama_index.readers.file import PyMuPDFReader
from llama_index.core.vector_stores import MetadataFilters, ExactMatchFilter
from llama_index.core.schema import BaseNode

from llama_index.postprocessor.sbert_rerank import SentenceTransformerRerank
from llama_index.core.query_engine import RetrieverQueryEngine

from app.models.files import KBFile

from llama_index.core.node_parser import SentenceWindowNodeParser
from llama_index.core.postprocessor import MetadataReplacementPostProcessor
from app.models.field_extraction import FieldExtraction
from llama_index.core.program import LLMTextCompletionProgram

from app.core.logger import get_logger
from typing import Optional

SENTENCE_WINDOW_PARSER = SentenceWindowNodeParser.from_defaults(window_size=3)
WINDOW_POST = MetadataReplacementPostProcessor(target_metadata_key="window")

class KnowledgeBaseWrapper:
    TOP_K = 6
    
    def __init__(self):
        self.async_client = get_qdrant_aclient()
        self.client = get_qdrant_client()
        self.base_settings = get_settings()
        self.vector_store = QdrantVectorStore(
            collection_name=self.base_settings.QDRANT_COLLECTION,
            client=self.client,
            aclient=self.async_client
        )
        self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
        
        self.index = VectorStoreIndex.from_vector_store(
            vector_store=self.vector_store,
        )
                
        self.reranker = SentenceTransformerRerank(
            model="cross-encoder/ms-marco-MiniLM-L-6-v2",
            top_n=6,
        )
                
        self.logger = get_logger(self.__class__.__name__)
        
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
        query_engine = await self.__build_query_engine(
            company_id=company_id, project_id=project_id, document_type=document_type, document_category=document_category, file_name=file_name, k=k
        )

        response = await query_engine.aquery(question)
        return response.response
    
    async def __build_query_engine(self, company_id: str, project_id: str, document_type: Optional[str] = None, document_category: Optional[str] = None, file_name: Optional[str] = None, k: int = 5) -> RetrieverQueryEngine:
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
        from llama_index.core.response_synthesizers.type import ResponseMode
        query_engine = RetrieverQueryEngine.from_args(
            retriever=retriever,
            node_postprocessors=[self.reranker]
        )
        
        return query_engine
    
    async def fill_a_field(self, company_id: str, project_id: str, system_prompt: str, user_prompt: str) -> str:
        full_prompt = system_prompt + "\n" + user_prompt
        return await self.query(question=full_prompt, company_id=company_id, project_id=project_id)
    
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
    
    def __build_context_snippets(self, nodes, max_chars_per_snip=600) -> str:
        def _snip(txt: str, n=max_chars_per_snip):
            return (txt[:n] + "..." if txt and len(txt) > n else txt)

        parts = []
        for i, sn in enumerate(nodes, start=1):
            node = sn.node if hasattr(sn, "node") else sn
            meta = node.metadata or {}
            file_name = meta.get("file_name")
            page_label = meta.get("source")
            parts.append(
                f"[{i}] file={file_name} page={page_label}\n{_snip(sn.node.get_content())}"
            )
            
        return "\n\n---\n\n".join(parts)
    
    def __transform_retrieved_value(self, extracted_value, field_type: str):
        if field_type == "array":
            print(str(extracted_value))
        if isinstance(extracted_value, list):
            # Remove duplicates
            unique_values = []
            seen = set()
            for v in extracted_value:
                if v not in seen:
                    unique_values.append(v)
                    seen.add(v)
            
            if len(unique_values) == 1:
                extracted_value = unique_values[0]
            else:
                if field_type == 'array':
                    extracted_value = unique_values
                else:
                    extracted_value = unique_values[0]
        return extracted_value
    
    async def __retrieve_context_for_field(self, company_id: str, project_id: str, instruction: str) -> str:
        query_engine = await self.__build_query_engine(company_id=company_id, project_id=project_id)
        from llama_index.core.schema import QueryBundle
        
        query = QueryBundle(query_str=instruction)
        nodes = await query_engine.aretrieve(query_bundle=query)
        windowed_nodes = WINDOW_POST.postprocess_nodes(nodes, query_str=instruction)
        top_nodes = windowed_nodes[:KnowledgeBaseWrapper.TOP_K]
        context = self.__build_context_snippets(top_nodes, max_chars_per_snip=1500)
        return context
    
    def __make_extraction_program(self):
        from llama_index.core.output_parsers.pydantic import PydanticOutputParser
        from llama_index.core.settings import Settings
        parser = PydanticOutputParser(output_cls=FieldExtraction)
        template = (
            "Jesteś asystentem do ekstrakcji danych. Używaj wyłącznie Kontekstu do odpowiedzi.\n"
            "Zadanie: {instruction}\n\n"
            "WAŻNE ZASADY:\n"
            "- Jeśli pole pojawia się z TĄ SAMĄ wartością wielokrotnie, zwróć tę pojedynczą wartość jako string\n"
            "- Jeśli pole pojawia się z RÓŻNYMI wartościami, zwróć je jako listę\n"
            "- Jeśli pole nie zostało znalezione lub masz wątpliwości, ustaw value=null i confidence=0\n"
            "- Ustaw confidence w zakresie od 0.0 (niepewne) do 1.0 (pewne)\n"
            "- Podaj krótkie uzasadnienie swojej ekstrakcji\n\n"
            "Zwróć ściśle JSON zgodny ze schematem: FieldExtraction(value, confidence, reasoning).\n\n"
            "Kontekst:\n{context}\n"
        )

        program = LLMTextCompletionProgram.from_defaults(
            output_parser=parser,
            prompt_template_str=template,
            llm=Settings.llm
        )

        return program
    
    async def extract_field(self, company_id: str, project_id: str, field_prompt: str, field_type: str) -> FieldExtraction:
        if field_type == "array":
            print(field_type)
        context = await self.__retrieve_context_for_field(
            company_id=company_id,
            project_id=project_id,
            instruction=field_prompt
        )
        program: LLMTextCompletionProgram = self.__make_extraction_program()
        result: FieldExtraction = await program.acall(
            instruction=field_prompt, context=context
        )
        
        extracted_value = self.__transform_retrieved_value(extracted_value=result.value, field_type=field_type)
        result.value = extracted_value
        return result
        
            
    
@lru_cache()
def get_knowledge_base_wrapper() -> KnowledgeBaseWrapper:
    return KnowledgeBaseWrapper()