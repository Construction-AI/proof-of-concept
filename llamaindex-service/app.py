import os
import time
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import qdrant_client
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    Settings
)
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core.node_parser import SentenceSplitter

app = FastAPI()

# Global variables
index = None
query_engine = None

class QueryRequest(BaseModel):
    query: str

class IndexRequest(BaseModel):
    directory_path: str

class StatusResponse(BaseModel):
    status: str
    message: str

def wait_for_qdrant():
    """Wait for Qdrant to be ready"""
    max_retries = 30
    retry_delay = 2
    
    for i in range(max_retries):
        try:
            client = qdrant_client.QdrantClient(
                host=os.getenv("QDRANT_HOST", "qdrant"),
                port=int(os.getenv("QDRANT_PORT", 6333))
            )
            client.get_collections()
            print("Successfully connected to Qdrant")
            return True
        except Exception as e:
            print(f"Waiting for Qdrant... ({i+1}/{max_retries}): {e}")
            time.sleep(retry_delay)
    
    return False

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    if not wait_for_qdrant():
        print("Failed to connect to Qdrant")
    else:
        print("LlamaIndex service ready")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.post("/index", response_model=StatusResponse)
async def create_index(request: IndexRequest):
    """Create embeddings from documents in the specified directory"""
    global index, query_engine
    
    try:
        # Validate directory path
        doc_path = Path(request.directory_path)
        if not doc_path.exists():
            raise HTTPException(status_code=400, detail=f"Directory not found: {request.directory_path}")
        
        # Load documents
        print(f"Loading documents from {request.directory_path}")
        documents = SimpleDirectoryReader(
            request.directory_path,
            recursive=True
        ).load_data()
        
        if not documents:
            raise HTTPException(status_code=400, detail="No documents found in the specified directory")
        
        print(f"Loaded {len(documents)} documents")
        
        # Initialize Qdrant client
        client = qdrant_client.QdrantClient(
            host=os.getenv("QDRANT_HOST", "qdrant"),
            port=int(os.getenv("QDRANT_PORT", 6333))
        )
        
        # Create collection if it doesn't exist
        collection_name = "documents"
        try:
            client.delete_collection(collection_name=collection_name)
        except:
            pass
        
        # Create vector store
        vector_store = QdrantVectorStore(
            client=client,
            collection_name=collection_name
        )
        
        # Create storage context
        storage_context = StorageContext.from_defaults(
            vector_store=vector_store
        )
        
        # Configure text splitter
        Settings.node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=50)
        
        # Create index
        print("Creating embeddings and storing in Qdrant...")
        index = VectorStoreIndex.from_documents(
            documents,
            storage_context=storage_context,
            show_progress=True
        )
        
        # Create query engine
        query_engine = index.as_query_engine()
        
        print("Indexing complete")
        return StatusResponse(
            status="success",
            message=f"Successfully indexed {len(documents)} documents"
        )
        
    except Exception as e:
        print(f"Error during indexing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
async def query_documents(request: QueryRequest):
    """Query the indexed documents"""
    global query_engine
    
    if query_engine is None:
        raise HTTPException(
            status_code=400,
            detail="No index available. Please create an index first using /index endpoint"
        )
    
    try:
        print(f"Querying: {request.query}")
        response = query_engine.query(request.query)
        
        return {
            "response": str(response),
            "source_nodes": [
                {
                    "text": node.node.get_content()[:200] + "...",
                    "score": node.score
                }
                for node in response.source_nodes
            ] if hasattr(response, 'source_nodes') else []
        }
        
    except Exception as e:
        print(f"Error during query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status")
async def get_status():
    """Check if index is ready"""
    return {
        "index_ready": index is not None,
        "query_engine_ready": query_engine is not None
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)