from app.infra.instances_qdrant import get_qdrant_aclient, get_qdrant_client
from app.core.config import get_settings
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core.storage import StorageContext
from llama_index.core import VectorStoreIndex

from app.models.files import LocalFile

class RagKnowledgeBase:
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
            vector_store=self.vector_store
        )
        
    def add_document(self, )
        