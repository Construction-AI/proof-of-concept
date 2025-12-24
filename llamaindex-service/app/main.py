from fastapi import FastAPI
from app.api.routes import (
    routes_health,
    routes_rag_engine_wrapper
)
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: code before yield
    # await startup_load_all_projects()
    
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
    app.include_router(routes_health.router, prefix="/health", tags=["Health Check"])
    app.include_router(routes_rag_engine_wrapper.router, prefix="/rag_engine", tags=["Rag Engine Wrapper"])
    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)