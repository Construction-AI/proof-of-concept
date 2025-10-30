from fastapi import FastAPI
from app.api import (
    routes_health,
    routes_index,
    routes_query,
    routes_field_extraction,
    routes_schema,
    routes_config
)
from app.utils.logging import get_logger

def create_app() -> FastAPI:
    app = FastAPI(
        title="LlamaIndex Service", 
        description="Document ingestion, indexing and querying API using LlamaIndex and Qdrant.",
        version="1.0.0"
        )

    # Register routes
    app.include_router(routes_health.router, tags=["System"])
    app.include_router(routes_index.router, prefix="/index", tags=["Indexing"])
    app.include_router(routes_query.router, prefix="/query", tags=['Query'])
    app.include_router(routes_field_extraction.router, prefix="/fill_field", tags=["Field Extraction"])
    app.include_router(routes_schema.router, prefix="/schema", tags=["Schema"])
    app.include_router(routes_config.router, prefix="/config", tags=["System", "Config"])

    import os
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
    logger = get_logger("Setup")
    logger.info("[Setup] Running in %s mode!", 'local' if LLM_PROVIDER == 'ollama' else 'online')

    return app

app = create_app()

if __name__ == "__main__":
    import asyncio
    print("DEBUG LOOP:", asyncio.get_running_loop())
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)