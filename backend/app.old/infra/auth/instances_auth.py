from functools import lru_cache
from app.api.services.auth_service import AuthService
import os
        
@lru_cache()
def get_auth_service():
    return AuthService(
        db_path=os.getenv("DATABASE_PATH"),
        secret_key=os.getenv("AUTH_SECRET_KEY")
    )