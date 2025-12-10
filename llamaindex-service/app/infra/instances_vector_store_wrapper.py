from typing import Optional
from qdrant_client import QdrantClient, AsyncQdrantClient
from app.core.logger import get_logger

class VectorStoreWrapper:
    def __init__(self, url: str, api_key: Optional[str] = None):
        self.client = QdrantClient(
            url=url,
            api_key=api_key,
            timeout=30
        )
        
        self.async_client = AsyncQdrantClient(
            url=url,
            api_key=api_key,
            timeout=30
        )
        
        self.logger = get_logger(self.__class__.__name__)
        
    async def check_collection_exists(self, collection_name: str) -> bool:
        return await self.async_client.collection_exists(collection_name=collection_name)
    
    async def delete_collection(self, collection_name: str):
        return await self.delete_collection(collection_name=collection_name)
    
    
