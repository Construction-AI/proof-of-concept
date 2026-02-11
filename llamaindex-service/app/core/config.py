from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Construction AI"
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str = "/data/database.db"
    
    # External APIs
    # OPENAI_API_KEY: str
    # QDRANT_URL: str
    # QDRANT_API_KEY: str
    
    MINIO_ENDPOINT: str 
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    
    # class Config:
    #     env_file = ".env"
    
settings = Settings()