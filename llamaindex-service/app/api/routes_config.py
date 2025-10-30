from fastapi import APIRouter
from pydantic import BaseModel
import os

router = APIRouter()

class ConfigResponse(BaseModel):
    mode: str # Ollama or OpenAI
    query_model: str
    embedding_model: str

@router.get("", response_model=ConfigResponse)
def get_config():
    """Simple config check endpoint"""
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
    embed_model = None
    query_model = None
    if LLM_PROVIDER == "ollama":
        embed_model = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
        query_model = os.getenv("OLLAMA_MODEL", "llama3:8b")
    elif LLM_PROVIDER == "openai":
        embed_model = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
        query_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    return ConfigResponse(
        mode=LLM_PROVIDER,
        query_model=query_model,
        embedding_model=embed_model
    )
