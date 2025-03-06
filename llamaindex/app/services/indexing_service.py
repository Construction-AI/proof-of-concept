import os
from pathlib import Path
import logging
from typing import List, Optional

from llama_index.core import Settings, SimpleDirectoryReader, StorageContext, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import Document
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama
from qdrant_client import QdrantClient

# Configure logging
logger = logging.getLogger(__name__)

class IndexingService:
    def __init__(
        self,
        documents_dir: str = "/data/documents",
        collection_name: str = "documents",
        chunk_size: int = 256,
        chunk_overlap: int = 10,
        ollama_base_url: Optional[str] = None,
        qdrant_url: Optional[str] = None,
        embedding_model: str = "nomic-embed-text",
        llm_model: str = "qwen2.5:14b",
    ):
        """
        Initialize the indexing service
        
        Args:
            documents_dir: Base directory for documents
            collection_name: Name of the Qdrant collection
            chunk_size: Size of text chunks for indexing
            chunk_overlap: Overlap between chunks
            ollama_base_url: Base URL for Ollama API
            qdrant_url: URL for Qdrant vector store
            embedding_model: Name of the embedding model to use
            llm_model: Name of the LLM model to use
        """
        self.documents_dir = Path(documents_dir)
        self.collection_name = collection_name
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Get environment variables if not provided
        self.ollama_base_url = ollama_base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.qdrant_url = qdrant_url or os.getenv("QDRANT_URL", "http://localhost:6333")
        
        self.embedding_model = embedding_model
        self.llm_model = llm_model
        
        # Create documents directory if it doesn't exist
        os.makedirs(self.documents_dir, exist_ok=True)
        
        # Initialize components
        self._initialize_components()
        
    def _initialize_components(self):
        """Initialize LlamaIndex components"""
        logger.info(f"Initializing components with Ollama URL: {self.ollama_base_url} and Qdrant URL: {self.qdrant_url}")
        
        # Configure embeddings and LLM
        embed_model = OllamaEmbedding(
            model_name=self.embedding_model,
            base_url=self.ollama_base_url
        )
        
        llm = Ollama(
            model=self.llm_model,
            base_url=self.ollama_base_url,
            request_timeout=120.0,
        )
        
        # Initialize Qdrant client
        self.qdrant_client = QdrantClient(url=self.qdrant_url)
        
        # Initialize vector store
        vector_store = QdrantVectorStore(
            client=self.qdrant_client,
            collection_name=self.collection_name,
        )
        
        # Configure storage context
        self.storage_context = StorageContext.from_defaults(vector_store=vector_store)
        
        # Configure global settings
        Settings.llm = llm
        Settings.embed_model = embed_model
        
    def process_directory(self):
        """
        Process documents from a specific directory
                    
        Returns:
            dict: Results of the processing
        """
        try:
            # Construct full directory path
            target_dir = self.documents_dir
                            
            # Load documents
            logger.info(f"Loading documents from: {target_dir}")
            reader = SimpleDirectoryReader(input_dir=str(target_dir))
            documents = reader.load_data()
            document_count = len(documents)
            
            if document_count == 0:
                logger.info(f"No documents found in directory: {target_dir}")
                return {
                    "status": "completed", 
                    "document_count": 0,
                    "message": "No documents found in the directory"
                }
            
            # Create index
            logger.info(f"Indexing {document_count} documents from: {target_dir}")
            index = VectorStoreIndex.from_documents(
                documents,
                storage_context=self.storage_context,
                embed_model=Settings.embed_model,
                transformations=[SentenceSplitter(chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap)]
            )
            
            return {
                "status": "completed",
                "document_count": document_count,
                "message": f"Successfully processed {document_count} documents"
            }
                
        except Exception as e:
            logger.error(f"Error processing directory")
            return {
                "status": "error",
                "message": f"Error processing directory: {str(e)}"
            }
    
    def query_index(self, query_text: str, num_results: int = 3):
        """Query the index with the given text"""
        try:
            # Recreate index from storage
            index = VectorStoreIndex.from_vector_store(
                self.storage_context.vector_store,
            )
            
            # Create query engine
            query_engine = index.as_query_engine(
                similarity_top_k=num_results,
            )
            
            # Execute query
            response = query_engine.query(query_text)
            return {
                "result": str(response),
                "source_nodes": [
                    {
                        "text": node.node.text,
                        "score": float(node.score) if hasattr(node, 'score') else None,
                        "document": node.node.metadata.get("file_name", "Unknown")
                    }
                    for node in response.source_nodes
                ] if hasattr(response, 'source_nodes') else []
            }
        except Exception as e:
            logger.error(f"Error querying index: {str(e)}")
            return {"status": "error", "message": str(e)}