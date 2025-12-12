from app.infra.instances_llamaindex import get_llamaindex_contexts
from app.infra.instances_qdrant import get_qdrant_aclient, get_qdrant_client
from pathlib import Path

from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core.storage.storage_context import StorageContext
from llama_index.core.retrievers import QueryFusionRetriever
from llama_index.retrievers.bm25 import BM25Retriever
from llama_index.postprocessor.sbert_rerank import SentenceTransformerRerank
from llama_index.core.query_engine import RetrieverQueryEngine

from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.readers.file import PyMuPDFReader
from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SentenceWindowNodeParser
from llama_index.core.postprocessor import MetadataReplacementPostProcessor

from app.core.project_engine import ProjectEngine

SENTENCE_WINDOW_PARSER = SentenceWindowNodeParser.from_defaults(window_size=3)
WINDOW_POST = MetadataReplacementPostProcessor(target_metadata_key="window")


PROJECT_ENGINES: dict[str, ProjectEngine] = {}

from app.core.logger import get_logger

def load_documents_with_metadata(input_dir: str):
    reader = SimpleDirectoryReader(
        input_dir=input_dir,
        recursive=True,
        filename_as_id=False,
        file_extractor={".pdf": PyMuPDFReader()},
    )
    docs = reader.load_data()
    for d in docs:
        d.metadata.setdefault("file_name", Path(d.metadata.get("file_path", d.doc_id)).name)
        d.metadata.setdefault("page_label", d.metadata.get("source", None))
    return docs

def index_documents(directory_path: str):
    ctx = get_llamaindex_contexts()

    docs = SimpleDirectoryReader(directory_path).load_data()

    index = VectorStoreIndex.from_documents(
        docs,
        storage_context=ctx["storage_context"],
    )

    index.storage_context.persist()

async def build_project_index(directory_path: str, project_id: str) -> ProjectEngine:
    documents = load_documents_with_metadata(directory_path)

    if not documents:
        raise ValueError(f"No documents found in {directory_path}")
    
    nodes = SENTENCE_WINDOW_PARSER.get_nodes_from_documents(documents=documents)

    qdrant_aclient = get_qdrant_aclient()
    qdrant_client = get_qdrant_client()

    try:
        await qdrant_aclient.delete_collection(project_id)
    except:
        pass

    vector_store = QdrantVectorStore(
        client=qdrant_client,
        aclient=qdrant_aclient,
        collection_name=project_id
    )
    
    storage_context = StorageContext.from_defaults(
        vector_store=vector_store
    )

    index = VectorStoreIndex(
        nodes=nodes,
        storage_context=storage_context,
        show_progress=True
    )

    bm25 = BM25Retriever.from_defaults(
        nodes=nodes,
        similarity_top_k=10
    )

    vector_retriver = index.as_retriever(similarity_top_k=10)

    fusion = QueryFusionRetriever(
        retrievers=[vector_retriver, bm25],
        mode="relative_score",
        num_queries=1,
        similarity_top_k=8,
    )

    reranker = SentenceTransformerRerank(
        model="cross-encoder/ms-marco-MiniLM-L-6-v2",
        top_n=6,
    )

    query_engine = RetrieverQueryEngine.from_args(
        retriever=fusion,
        node_postprocessors=[WINDOW_POST, reranker],
        response_mode="compact",
    )

    return ProjectEngine(
        index=index, nodes=nodes, retriever=fusion, query_engine=query_engine
    )

def load_project_index(project_id: str) -> ProjectEngine:
    aclient = get_qdrant_aclient()
    client = get_qdrant_client()

    collection_name = project_id

    vector_store = QdrantVectorStore(
        client=client,
        aclient=aclient,
        collection_name=collection_name,
    )

    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        storage_context=storage_context,
        show_progress=False
    )

    nodes = list(index.docstore.docs.values())
    bm25 = None
    if nodes:
        bm25 = BM25Retriever.from_defaults(
            nodes=nodes,
            similarity_top_k=10
        )

    vector_retriever = index.as_retriever(similarity_top_k=10)

    fusion = None
    if bm25:
        fusion = QueryFusionRetriever(
            retrievers=[vector_retriever, bm25],
            mode="relative_score",
            num_queries=1,
            similarity_top_k=8,
        )
    else:
        fusion = QueryFusionRetriever(
            retrievers=[vector_retriever],
            mode="relative_score",
            num_queries=1,
            similarity_top_k=8,
        )

    reranker = SentenceTransformerRerank(
        model="cross-encoder/ms-marco-MiniLM-L-6-v2",
        top_n=6,
    )

    query_engine = RetrieverQueryEngine.from_args(
        retriever=fusion,
        node_postprocessors=[WINDOW_POST, reranker],
        response_mode="compact",
    )

    return ProjectEngine(
        index=index,
        nodes=None,
        retriever=fusion,
        query_engine=query_engine

    )

async def list_projects_in_qdrant():
    aclient = get_qdrant_aclient()
    result = []

    try:
        collections = await aclient.get_collections()
        for coll in collections.collections:
            result.append(coll.name)
        return result
    except Exception as e:
        print(f"Failed to get all collections: {str(e)}")
        raise e
    
async def startup_load_all_projects():
    logger = get_logger("Document loader")
    try:
        projects = await list_projects_in_qdrant()
        if not projects:
            logger.warning("No projects were found.")
            return 
        for project_id in projects:
            PROJECT_ENGINES[project_id] = load_project_index(project_id=project_id)
        logger.info("The projects have been loaded successfully.")
    except Exception as e:
        logger.error(f"Failed to load projects: {str(e)}")
    
