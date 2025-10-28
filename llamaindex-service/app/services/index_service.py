import os
from pathlib import Path
from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core.retrievers import QueryFusionRetriever
from llama_index.retrievers.bm25 import BM25Retriever
from llama_index.postprocessor.sbert_rerank import SentenceTransformerRerank
from llama_index.core.query_engine import RetrieverQueryEngine
from qdrant_client import QdrantClient, AsyncQdrantClient

from app.core.document_loader import load_documents_with_metadata
from llama_index.core.node_parser import SentenceWindowNodeParser
from llama_index.core.postprocessor import MetadataReplacementPostProcessor
from app.utils.logging import get_logger

from typing import Dict, List

SENTENCE_WINDOW_PARSER = SentenceWindowNodeParser.from_defaults(window_size=3)
WINDOW_POST = MetadataReplacementPostProcessor(target_metadata_key="window")

indices: Dict[str, VectorStoreIndex] = {}
query_engines: Dict[str, RetrieverQueryEngine] = {}
project_nodes: Dict[str, List] = {}  # do BM25 i cytatów
retrievers: Dict[str, QueryFusionRetriever] = {}

def build_project_index(directory_path: str, project_id: str):
    logger = get_logger("Index")
    """Build hybrid retrieval index for a project."""
    # 1) Ładowanie
    documents = load_documents_with_metadata(directory_path)
    if not documents:
        raise ValueError("No documents found")

    # 2) Tworzenie węzłów (nodes)
    nodes = SENTENCE_WINDOW_PARSER.get_nodes_from_documents(documents)
    # nodes = enrich_nodes_with_headings(nodes)

    # 3) Qdrant – osobna kolekcja na projekt
    qdrant_host = os.getenv("QDRANT_HOST", "qdrant")
    qdrant_port = int(os.getenv("QDRANT_PORT", 6333))
    client = QdrantClient(
        host=qdrant_host,
        port=qdrant_port,
        timeout=30,
    )
    aclient = AsyncQdrantClient(host=qdrant_host, port=qdrant_port, timeout=30)
    collection_name = f"proj_{project_id}"
    # Nie kasujemy w ciemno – pozwalamy nadpisać przez nowy ingest; jeśli trzeba wyczyścić, zrób to celowo
    try:
        client.get_collection(collection_name)
        print(f"Collection '{collection_name}' exists – upserting.")
    except Exception:
        print(f"Creating collection '{collection_name}'")

    vector_store = QdrantVectorStore(client=client, aclient=aclient, collection_name=collection_name)

    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    # 4) Budowa indeksu wektorowego
    index = VectorStoreIndex(
        nodes=nodes,
        storage_context=storage_context,
        show_progress=True
    )

    # 5) BM25 na tych samych węzłach (bez wektoryzacji)
    bm25 = BM25Retriever.from_defaults(nodes=nodes, similarity_top_k=10)

    # 6) Fusion retriever (wektory + BM25)
    vector_retriever = index.as_retriever(similarity_top_k=10)

    fusion = QueryFusionRetriever(
        retrievers=[vector_retriever, bm25],
        # relative fusion dobrze się sprawdza w praktyce
        mode="relative_score",
        num_queries=1,
        similarity_top_k=8,
        verbose=False,
    )

    # 7) Reranker (cross-encoder, mały i szybki)
    reranker = SentenceTransformerRerank(
        model="cross-encoder/ms-marco-MiniLM-L-6-v2",
        top_n=6
    )

    # 8) Query engine (może korzystać z LLM; jeśli Settings.llm=None – zwróci głównie źródła)
    query_engine = RetrieverQueryEngine.from_args(
        retriever=fusion,
        node_postprocessors=[WINDOW_POST, reranker], # IMPORTANT: window first, the rerank or vice versa; both work
        response_mode="compact",
    )

    # 9) Zapis do rejestrów
    indices[project_id] = index
    query_engines[project_id] = query_engine
    project_nodes[project_id] = nodes
    retrievers[project_id] = fusion
    