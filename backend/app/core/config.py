from pydantic_settings import BaseSettings
from typing import Literal, Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Construction AI"

    SERVICE_NAME: str = "API Service"
    APP_VERSION: str

    BUCKET_COLLECTION_NAME: str = "construction-docs"
    UPLOAD_DIR: str = "/uploads"
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    
    # Database
    DATABASE_URL: str = "/data/database.db"
    
    # External APIs (either LOCAL or REMOTE)
    LLM_PROVIDER: Literal["OPENAI", "LMSTUDIO"]
    LLM_PROVIDER_API_KEY: Optional[str]
    LLM_PROVIDER_BASE_URL: Optional[str]
    LLM_MODEL: str
    LLM_EMBEDDING_MODEL: str
    
    # Vector Store (Qdrant)
    QDRANT_URL: str
    QDRANT_API_KEY: str | None = None
    QDRANT_RERANKER_MODEL: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    QDRANT_RERANKER_TOP_N: int = 6
    EMBEDDING_DIMENSION: int
    
    MINIO_ENDPOINT: str 
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
            
    
settings = Settings() # type: ignore