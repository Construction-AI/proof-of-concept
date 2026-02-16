from pydantic_settings import BaseSettings

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
    
    # External APIs
    OPENAI_API_KEY: str
    MODEL: str
    EMBEDDING_MODEL: str
    
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