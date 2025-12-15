from functools import lru_cache
from qdrant_client import QdrantClient, AsyncQdrantClient
from app.core.settings import get_settings

@lru_cache()
def get_qdrant_client() -> QdrantClient:
    settings = get_settings()
    client = QdrantClient(
        location=settings.QDRANT_URL,
        timeout=30
    )
    return client

@lru_cache()
def get_qdrant_aclient() -> AsyncQdrantClient:
    settings = get_settings()
    client = AsyncQdrantClient(
        location=settings.QDRANT_URL,
        timeout=30
    )
    return client