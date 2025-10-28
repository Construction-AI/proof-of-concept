import os
import time
from pathlib import Path
from typing import Dict, List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from llama_index.core import (
    VectorStoreIndex,
    StorageContext,
    Settings,
)
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.readers.file import PyMuPDFReader
from llama_index.core import SimpleDirectoryReader
from llama_index.core.retrievers import QueryFusionRetriever
from llama_index.postprocessor.sbert_rerank import SentenceTransformerRerank
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.retrievers.bm25 import BM25Retriever
from qdrant_client import QdrantClient, AsyncQdrantClient

from node_enrichment import enrich_nodes_with_headings
from llama_index.core.program import LLMTextCompletionProgram
from llama_index.core.output_parsers import PydanticOutputParser
from structured_output import FieldExtraction, FillFieldResponse, FillFieldRequest

from schema_loader import load_schema, flatten_fields, get_field_def
from fastapi import Query

from llama_index.core.node_parser import SentenceWindowNodeParser
from llama_index.core.postprocessor import MetadataReplacementPostProcessor

SENTENCE_WINDOW_PARSER = SentenceWindowNodeParser.from_defaults(
    window_size=3, # 3 sentences around the hit; tune 2-5
    window_metadata_key="window", # where the passage is stored
    original_text_metadata_key="orig" # keep original if needed
)

WINDOW_POST = MetadataReplacementPostProcessor(
    target_metadata_key="window" # swap node text -> window passage
)

# LLM (wybór przez env)
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")  # "ollama" lub "openai"
if LLM_PROVIDER.lower() == "ollama":
    from llama_index.llms.ollama import Ollama
    Settings.llm = Ollama(model=os.getenv("OLLAMA_MODEL", "llama3"))
elif LLM_PROVIDER.lower() == "openai":
    from llama_index.llms.openai import OpenAI
    Settings.llm = OpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
else:
    Settings.llm = None  # tylko retrieval (bez syntezy)

# Embeddings – wielojęzyczne (PL/EN)
embed_model=os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
Settings.embed_model = HuggingFaceEmbedding(model_name=embed_model)

# Parser – większe, logiczne chunki
NODE_PARSER = SentenceSplitter(chunk_size=1000, chunk_overlap=120)

app = FastAPI()

# Rejestry per projekt
indices: Dict[str, VectorStoreIndex] = {}
query_engines: Dict[str, RetrieverQueryEngine] = {}
project_nodes: Dict[str, List] = {}  # do BM25 i cytatów
retrievers: Dict[str, QueryFusionRetriever] = {}

# MODELE REQUEST/RESPONSE
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
            client = QdrantClient(
                host=os.getenv("QDRANT_HOST", "qdrant"),
                port=int(os.getenv("QDRANT_PORT", 6333)),
                timeout=10,
            )
            client.get_collections()
            print("Successfully connected to Qdrant")
            return True
        except Exception as e:
            print(f"Waiting for Qdrant... ({i+1}/{max_retries}): {e}")
            time.sleep(retry_delay)
    return False

def build_context_snippets(nodes, max_chars_per_snip=600):
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
    
def make_extraction_program():
    parser = PydanticOutputParser(output_cls=FieldExtraction)
    template = (
        "You are an extraction assistant. Use only the Context to answer.\n"
        "Task: {instruction}\n\n"
        "IMPORTANT RULES:\n"
        "- If the field appears with the SAME value multiple times, return that single value as a string\n"
        "- If the field appears with DIFFERENT values, return them as a list\n"
        "- If the field is not found or uncertain, set value=null and confidence=0\n"
        "- Set confidence between 0.0 (uncertain) and 1.0 (certain)\n"
        "- Provide brief reasoning for your extraction\n\n"
        "Return strictly a JSON matching the schema: FieldExtraction(value, confidence, reasoning).\n\n"
        "Context:\n{context}\n"
    )
    program = LLMTextCompletionProgram.from_defaults(
        output_parser=parser,
        prompt_template_str=template,
        llm=Settings.llm,
    )
    return program


@app.post("/fill_field", response_model=FillFieldResponse)
async def fill_field(req: FillFieldRequest):
    pid = req.project_id
    if not pid in retrievers:
        raise HTTPException(status_code=400, detail=f"No index for project_id='{pid}'. Create it with /index.")
    try:
        # 0) Check if field exists
        field_def = get_field_def(req.field_id)
        if not field_def:
            raise HTTPException(status_code=400, detail=f"Unknown field_id: {req.field_id}")

        # 1) Retrieve and rerank
        fusion = retrievers[pid]
        nodes = fusion.retrieve(req.instruction)

        # apply sentence-window replacement
        windowed_nodes = WINDOW_POST.postprocess_nodes(nodes, query_str=req.instruction)

        # 2) Build context
        top_nodes = windowed_nodes[: req.top_k]
        context = build_context_snippets(top_nodes, max_chars_per_snip=1500)

        # 3) Run extraction
        program = make_extraction_program()
        result: FieldExtraction = program(
            instruction=req.instruction, context=context
        )

        # 4) Normalize the value - if it's a list with all same values, pick the first one
        extracted_value = result.value
        if isinstance(extracted_value, list):
            # Remove duplicates while preserving order
            unique_values = []
            seen = set()
            for v in extracted_value:
                if v not in seen:
                    unique_values.append(v)
                    seen.add(v)
            
            # If all values are the same (or only one unique), return single value
            if len(unique_values) == 1:
                extracted_value = unique_values[0]
            else:
                # Multiple different values - you could either:
                # 1. Return the first one (most common/highest confidence)
                # 2. Join them (e.g., "C25/30, C8/10")
                # 3. Keep as list if FillFieldResponse supports it
                extracted_value = unique_values[0]  # Take the most relevant (first retrieved)
                print(f"Warning: Multiple different values found for {req.field_id}: {unique_values}")

        # 5) Build sources
        src = []
        for sn in top_nodes:
            meta = sn.node.metadata or {}
            content = sn.node.get_content() or ""
            excerpt = content if len(content) <= 2000 else (content[:2000] + "...")
            
            src.append({
                "file_name": meta.get("file_name"),
                "page_label": meta.get("source"),
                "score": sn.score,
                "excerpt": excerpt
            })
        
        return FillFieldResponse(
            field_id=req.field_id,
            value=extracted_value,
            confidence=float(result.confidence or 0.0),
            sources=src
        )
    except Exception as e:
        print(f"Error in /fill_field: {e}")
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/health")
async def health_check():
    return {"status": "healthy"}

def load_documents_with_metadata(input_dir: str):
    """
    Ładuje dokumenty. Dla PDF używa PyMuPDFReader (strona=>osobny Document),
    dzięki czemu w metadata mamy 'file_name' i 'page_label'.
    """
    reader = SimpleDirectoryReader(
        input_dir=input_dir,
        recursive=True,
        filename_as_id=False,
        file_extractor={".pdf": PyMuPDFReader()},
    )
    docs = reader.load_data()
    # Upewnijmy się, że mamy przydatne metadane
    for d in docs:
        d.metadata.setdefault("file_name", Path(d.metadata.get("file_path", d.doc_id)).name)
        d.metadata.setdefault("page_label", d.metadata.get("source", None))
    return docs

def build_project_index(directory_path: str, project_id: str):
    """
    Buduje indeks dla projektu:
    - węzły z metadanymi (doc_id, file_name, page_label),
    - Qdrant jako wektorówka,
    - BM25 na tych samych węzłach,
    - retriever hybrydowy + reranker + query engine.
    """
    global fusion

    # 1) Ładowanie
    documents = load_documents_with_metadata(directory_path)
    if not documents:
        raise ValueError("No documents found")

    # 2) Tworzenie węzłów (nodes)
    nodes = SENTENCE_WINDOW_PARSER.get_nodes_from_documents(documents)
    nodes = enrich_nodes_with_headings(nodes)

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

@app.post("/index", response_model=StatusResponse)
async def create_index(request: IndexRequest):
    doc_path = Path(request.directory_path)
    if not doc_path.exists():
        raise HTTPException(status_code=400, detail=f"Directory not found: {request.directory_path}")
    try:
        print("Building project index...")
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
        raise HTTPException(
            status_code=400,
            detail=f"No index for project_id='{project_id}'. Create it with /index."
        )
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

@app.get("/schema")
async def get_schema():
    return load_schema()

@app.get("/fields")
async def list_fields():
    return flatten_fields(load_schema())

@app.get("/fields/search")
async def search_fields(q: str = Query("", min_length=1)):
    ql = q.lower()
    reg = flatten_fields(load_schema())
    return [f for f in reg if ql in f["field_id"].lower() or ql in (f.get("label") or "").lower()][:200]

import sys

print("=== LlamaIndex container booting ===", flush=True)
print(f"Python version: {sys.version}", flush=True)
print(f"LLM_PROVIDER={LLM_PROVIDER}", flush=True)
print(f"QDRANT_HOST={os.getenv('QDRANT_HOST')}", flush=True)
print(f"OPENAI_API_KEY={'set' if os.getenv('OPENAI_API_KEY') else 'missing'}", flush=True)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)