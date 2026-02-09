from functools import lru_cache
from openai import OpenAI
from app.core.settings import get_settings

@lru_cache()
def get_openai_client() -> OpenAI:
    settings = get_settings()
    return OpenAI(api_key=settings.OPENAI_API_KEY)