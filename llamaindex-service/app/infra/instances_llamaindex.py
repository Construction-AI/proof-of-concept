from functools import lru_cache
from llama_index.core import StorageContext, ServiceContext
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from app.core.settings import get_settings
from app.infra.clients.instances_qdrant import get_qdrant_client
from llama_index.vector_stores.qdrant import QdrantVectorStore

@lru_cache()
def get_llamaindex_contexts():
    settings = get_settings()
    qdrant = get_qdrant_client()

    embed_model = OpenAIEmbedding(
        model=settings.EMBEDDING_MODEL,
        api_key=settings.OPENAI_API_KEY,
        dimensions=settings.EMBEDDING_DIMENSION
    )

    vector_store = QdrantVectorStore(
        client=qdrant,
        collection_name=settings.QDRANT_COLLECTION,
    )

    storage_context = StorageContext.from_defaults(
        vector_store=vector_store
    )

    llm = OpenAI(
        model=settings.OPENAI_MODEL,
        api_key=settings.OPENAI_API_KEY,
        temperature=0,
    )

    from llama_index.core.settings import Settings as LLSettings
    LLSettings.llm = llm
    LLSettings.embed_model = embed_model

    return {
        "storage_context": storage_context,
        "embed_model": embed_model,
        "vector_store": vector_store
    }