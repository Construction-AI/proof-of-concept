from app.infra.instances_qdrant import get_qdrant_client
from app.core.config import get_settings

def recreate_collection(dim: int):
    qdrant = get_qdrant_client()
    settings = get_settings()

    qdrant.recreate_collection(
        collection_name=settings.QDRANT_COLLECTION,
        vectors_config={"size": dim, "distance": "Cosine"}
    )

def insert_vectors(vectors: list, payloads: list):
    qdrant = get_qdrant_client()
    settings = get_settings()

    qdrant.upsert(
        collection_name=settings.QDRANT_COLLECTION,
        points=vectors,
        payloads=payloads
    )