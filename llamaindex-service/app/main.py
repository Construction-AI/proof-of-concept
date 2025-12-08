from fastapi import FastAPI
from app.api.routes import (
    routes_document_loader,
    routes_query,
    routes_filling,
    routes_project_extractor,
    routes_file_manager,
    routes_health,
    routes_vector_store_manager
)
from app.api.services.document_loader import startup_load_all_projects
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
    app.include_router(routes_filling.router, prefix="/filling", tags=["Filling Engine"])
    app.include_router(routes_project_extractor.router, prefix="/project_extractor", tags=["Project Extractor"])
    app.include_router(routes_file_manager.router, prefix="/file_manager", tags=["File Manager"])
    app.include_router(routes_health.router, prefix="/health", tags=["Health Check"])
    app.include_router(routes_vector_store_manager.router, prefix="/vector_store_manager", tags=["Vector Store Manager"])

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)