from llama_index.core import VectorStoreIndex
from app.infra.instances_llamaindex import get_llamaindex_contexts
from app.api.services.document_loader import PROJECT_ENGINES

def query_rag(question: str) -> str:
    ctx = get_llamaindex_contexts()

    index = VectorStoreIndex.from_vector_store(
        ctx["vector_store"],
        storage_context=ctx["storage_context"]
    )

    query_engine = index.as_query_engine(
        similarity_top_k=5,
        response_mode="compact"
    )

    return query_engine.query(question).response

def query_project(project_id: str, question: str):
    engine = PROJECT_ENGINES[project_id].query_engine
    return engine.query(question)