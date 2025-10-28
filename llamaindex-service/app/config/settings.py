import os
from pydantic_settings import BaseSettings


class ServerSettings(BaseSettings):
    """Global configuration."""
    environment: str = os.getenv("ENV", "development")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

server_settings = ServerSettings()