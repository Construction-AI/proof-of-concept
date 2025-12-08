from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):
    # -- API --
    API_PORT: int = 8000
    API_HOST: str = "0.0.0.0"

    # -- OpenAI --
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = "gpt-4.1"

    # -- Qdrant --
    QDRANT_URL: str = os.getenv("QDRANT_URL")
    QDRANT_API_KEY: str | None = None
    QDRANT_COLLECTION: str = "documents"

    # -- Embeddings --
    EMBEDDING_MODEL: str = os.getenv("intfloat/multilingual-e5-large") or "text-embedding-3-large"
    EMBEDDING_DIMENSION: int = 3072

    # -- LlamaIndex -- 
    CHUNK_SIZE: int = 2048
    CHUNK_OVERLAP: int = 200

    # -- Paths --
    TEMP_UPLOAD_DIR: str = "/tmp/uploads"

    # -- MinIO --
    MINIO_URL: str = os.getenv("MINIO_URL")
    MINIO_ENDPOINT: str = os.getenv("MINIO_ENDPOINT")
    MINIO_ACCESS_KEY: str = os.getenv("MINIO_ROOT_USER")
    MINIO_SECRET_KEY: str = os.getenv("MINIO_ROOT_PASSWORD")

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
