import os
import time
from pathlib import Path
from typing import Dict, List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

import qdrant_client

from llama_index.core import (
    VectorStoreIndex,
    StorageContext,
    Settings
)
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.readers.file import PyMuPDFReader
from llama_index.core import SimpleDirectoryReader
from llama_index.core.retrievers import QueryFusionRetriever
from llama_index.retrievers.bm25 import BM25Retriever
from llama_index.postprocessor.sbert_rerank import SentenceTransformerRerank
from llama_index.core.query_engine import RetrieverQueryEngine

# LLM (chosen via .env)
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama") # "ollama" or "openai"
if LLM_PROVIDER.lower() == "ollama":
    from llama_index.llms.ollama import Ollama
    Settings.llm = Ollama(model=os.getenv("OLLAMA_MODEL", "llama3"))
elif LLM_PROVIDER.lower() == "openai":
    from llama_index.llms.openai import OpenAI
    Settings.llm = OpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
else:
    Settings.llm = None # only retrieval (no synthesis)

# Embeddings - multilang (PL / EN)
EMBEDDING_MODEL="intfloat/multilingual-e5-large"
Settings.embed_model = HuggingFaceEmbedding(EMBEDDING_MODEL)

# Parser
NODE_PARSER = SentenceSplitter(chunk_size=1000, chunk_overlap=120)

app = FastAPI()

# Per Project Registers
indices: Dict[str, VectorStoreIndex] = {}
query_engines: Dict[str, RetrieverQueryEngine] = {}
project_nodes: Dict[str, List] = {} # for BM25 and quoting

# MODEL Request/Response
class QueryRequest(BaseModel):
    query: str
    project_id: str

class IndexRequest(BaseModel):
    directory_path: str
    project_id: str

class StatusResponse(BaseModel):
    status: str
    message: str

def wait_for_qdrant() -> bool:
    max_retries = 30
    retry_delay = 2
    for i in range(max_retries):
        try:
            client = qdrant_client.QdrantClient(
                host=os.getenv("QDRANT_HOST", "qdrant"),
                port=int(os.getenv("QDRANT_PORT", 6333)),
                timeout=10
            )
            client.get_collections()
            print("Successfully connected to Qdrant")
            return True
        except Exception as e:
            print(f"Waiting for Qdrant... ({i + 1}/{max_retries}): {e}")
            time.sleep(retry_delay)
    return False

@app.on_event("startup")
async def startup_event():
    print("==> STARTUP: waiting for Qdrant...")
    if not wait_for_qdrant():
        print("==> Qdrant connection failed")
    else:
        print("==> LlamaIndex service ready and listening on 0.0.0.0:8000")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

def load_documents_with_metadata(input_dir: str):
    """
    Loads documents. For PDF it uses PyMuPDFReader (page -> separate document),
    thanks to this in metadata we have 'file_name' and 'page_label'
    """
    reader = SimpleDirectoryReader(
        input_dir=input_dir,
        recursive=True,
        filename_as_id=False,
        file_extractor={".pdf": PyMuPDFReader()}
    )
    docs = reader.load_data()
    
    # Make sure we have useful metadata
    for d in docs:
        d.metadata.setdefault("file_name", Path(d.metadata.get("file_path", d.doc_id).name))
        d.metadata.setdefault("page_label", d.metadata.get("page_label", None))
    return docs

def build_project_index(directory_path: str, project_id: str):
    """
    Builds project index:
    - nodes with metadata (doc_id, file_name, page_label)
    - Qdrant as Vector Store
    - BM25 on the same nodes
    - hybrid retriever + reranker + quer engine.
    """

    # 1) Loading
    documents = load_documents_with_metadata(directory_path)
    if not documents:
        raise ValueError("No documents found")
    
    # 2) Creating nodes
    nodes = NODE_PARSER.get_nodes_from_documents(documents)

    # 3) Qdrant - separate collection for each project
    client = qdrant_client.QdrantClient(
        host = os.getenv("QDRANT_HOST", "qdrant"),
        port = int(os.getenv("QDRANT_PORT", 6333)),
        timeout=30,
    )
    collection_name = f"proj_{project_id}"

    # We don't delete blindly - we let to overwrite with new ingest; if we need to clean do it purposefully
    try:
        client.get_collection(collection_name)
        print(f"Collection '{collection_name}' exists - upserting.")
    except Exception:
        print(f"Creating collection '{collection_name}'")

    vector_store = QdrantVectorStore(client=client, collection_name=collection_name)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    # 4) Build vector index
    index = VectorStoreIndex(nodes=nodes, storage_context=storage_context, show_progress=True)

    # 5) BM25 on the same nodes (no vectorization)
    bm25 = BM25Retriever.from_defaults(nodes=nodes, similarity_top_k=10)

    # 6) Fusion retriever (vectors + BM25)
    vector_retriever = index.as_retriever(similarity_top_k=10)
    fusion = QueryFusionRetriever(
        retrievers=[vector_retriever, bm25],
        mode="relative_score",
        num_queries=1,
        similarity_top_k=8,
        verbose=False,
    )

    # 7) Reranker (cross-encoder, small and quick)
    reranker = SentenceTransformerRerank(
        model="cross-encoder/ms-marco-MiniLM-L-6-v2",
        top_n=6
    )

    # 8) Query engine (can use LLM; if Settings.llm=None - it will return main sources)
    query_engine = RetrieverQueryEngine.from_args(
        retriever=fusion,
        node_postprocessors=[reranker],
        response_mode="compact"
    )

    # 9) Write to registers
    indices[project_id] = index
    query_engines[project_id] = query_engine
    project_nodes[project_id] = nodes


@app.post('/index', response_model=StatusResponse)
async def create_index(request: IndexRequest):
    doc_path = Path(request.directory_path)
    if not doc_path.exists():
        raise HTTPException(status_code=400, detail=f"Directory not found: {request.directory_path}")
    try:
        build_project_index(request.directory_path, request.project_id)
        return StatusResponse(
            status="success",
            message=f"Indexed project '{request.project_id}' from {request.directory_path}"
        )
    except Exception as e:
        print(f"Error during indexing: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/query")
async def query_documents(request: QueryRequest):
    project_id = request.project_id
    if project_id not in query_engines:
        raise HTTPException(status_code=400, detail=f"No index for project_id='{project_id}'. Create it with /index")
    try:
        qe = query_engines[project_id]
        response = qe.query(request.query)

        def _snip(txt: str, n=300):
            return (txt[:n] + "...") if txt and len(txt) > n else txt
    
        source_nodes = []
        if hasattr(response, "source_nodes"):
            for sn in response.source_nodes:
                meta = sn.node.metadata or {}
                source_nodes.append({
                    "file_name": meta.get("file_name"),
                    "page_label": meta.get("page_label"),
                    "score": sn.score,
                    "excerpt": _snip(sn.node.get_content())
                })
        return {
            "response": str(response),
            "source_nodes": source_nodes
        }
    except Exception as e:
        print(f"Error during query: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/status")
async def get_status():
    return {
        "projects": list(indices.keys()),
        "ready": {pid: True for pid in indices.keys()},
        "llm_provider": LLM_PROVIDER
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
