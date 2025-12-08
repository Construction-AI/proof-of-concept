from functools import lru_cache
from qdrant_client import QdrantClient, AsyncQdrantClient, models
from app.core.config import get_settings
from app.core.logger import get_logger
from typing import Optional
import datetime

class QdrantClientWrapper:
    def __init__(self, url: str):
        self.client = QdrantClient(
            url=url,
            timeout=30
        )
        self.async_client = AsyncQdrantClient(
            url=url,
            timeout=30
        )
        self.logger = get_logger("QdrantClientWrapper")

    async def check_collection_exists(self, collection_name: str) -> bool:
        return await self.async_client.collection_exists(collection_name=collection_name)

    # Create empty collection with given `collection_name`
    async def create_collection(self, collection_name: str, vector_size: Optional[int] = 100):
        await self.async_client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(size=vector_size, distance=models.Distance.COSINE)
        )
    
    # Delete and create empty collection with given `collection_name`
    async def recreate_collection(self, collection_name: str, vector_size: Optional[int] = 100):
        await self.async_client.recreate_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(size=vector_size, distance=models.Distance.COSINE)
        )

    async def insert_vectors(self, collection_name: str, vectors: list):
        await self.async_client.upsert(
            collection_name=collection_name,
            points=vectors,
            # payloads=payloads
        )
        self.logger.info(f"Vectors successfully inserted into {collection_name}")

    def create_point(self, id: int, vector: list, project_id: str, is_schema: bool, document_type: str, file_url: Optional[str]) -> models.PointStruct:
        payload = {
            "project_id": project_id,
            "is_schema": is_schema,
            "document_type": document_type,
            "file_url": file_url,
            "last_modified": datetime.datetime.now()
        }
        return models.PointStruct(
            id=id,
            vector=vector,
            payload=payload
        )
    

@lru_cache()
def get_qdrant_client_wrapper() -> QdrantClientWrapper:
    settings = get_settings()
    return QdrantClientWrapper(
        url=settings.QDRANT_URL
    )

@lru_cache()
def get_qdrant_client() -> QdrantClient:
    qdrant_client_wrapper = get_qdrant_client_wrapper()
    return qdrant_client_wrapper.client

@lru_cache()
def get_qdrant_aclient() -> AsyncQdrantClient:
    qdrant_client_wrapper = get_qdrant_client_wrapper()
    return qdrant_client_wrapper.async_client