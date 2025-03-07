import os
from pydantic_settings import BaseSettings

# Get the project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class Settings(BaseSettings):
    # API settings
    API_TITLE: str = "Document Processing API"
    API_DESCRIPTION: str = "API for processing and querying documents using LlamaIndex and Qdrant"
    API_VERSION: str = "1.0.0"
    
    # Server settings
    HOST: str = os.getenv("LLAMAINDEX_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("LLAMAINDEX_PORT", "8000"))
    
    # Directory paths
    PROJECT_ROOT: str = PROJECT_ROOT
    LOG_DIR: str = os.path.join(PROJECT_ROOT, "logs")
    DOCUMENTS_DIR: str = os.path.join("/", "data", "documents")
    INDEXES_DIR: str = os.path.join("/", "data", "indexes")
    
    # CORS settings
    CORS_ALLOW_ORIGINS: list = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list = ["*"]
    CORS_ALLOW_HEADERS: list = ["*"]
    
# Create settings instance
settings = Settings()

# Create necessary directories
os.makedirs(settings.LOG_DIR, exist_ok=True)