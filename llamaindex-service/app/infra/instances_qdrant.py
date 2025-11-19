from functools import lru_cache
from qdrant_client import QdrantClient, AsyncQdrantClient
from app.core.config import get_settings

@lru_cache()
def get_qdrant_client() -> QdrantClient:
    settings = get_settings()
    return QdrantClient(
        url=settings.QDRANT_URL,
        timeout=30
    )

@lru_cache()
def get_qdrant_aclient() -> AsyncQdrantClient:
    settings = get_settings()
    return AsyncQdrantClient(
        url=settings.QDRANT_URL,
        timeout=30
    )