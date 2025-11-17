from fastapi import FastAPI
from app.routes import (
    routes_document_loader,
    routes_query
)
from app.services.document_loader import startup_load_all_projects
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: code before yield
    await startup_load_all_projects()
    
    yield
    
    # Shutdown: code after yield (if you need cleanup)
    # Add any cleanup code here if needed
    pass

def create_app() -> FastAPI:
    app = FastAPI(
        title="LlamaIndex Service", 
        description="Document ingestion, indexing and querying API using LlamaIndex and Qdrant.",
        version="1.0.0",
        lifespan=lifespan
        )

    # Register routes

    app.include_router(routes_document_loader.router, prefix="/index", tags=["Documents loader"])
    app.include_router(routes_query.router, prefix="/query", tags=["Query Engine"])

    # import os
    # LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
    # logger = get_logger("Setup")
    # logger.info("[Setup] Running in %s mode!", 'local' if LLM_PROVIDER == 'ollama' else 'online')

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)