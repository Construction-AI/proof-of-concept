from fastapi import FastAPI, APIRouter
from app.api.routes import (
    routes_health,
    routes_database,
    routes_rag_engine_wrapper,
    routes_auth
)
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

def create_app() -> FastAPI:
    app = FastAPI(
        title="LlamaIndex Service",
        description="Document ingestion, indexing and querying API using LlamaIndex and Qdrant.",
        version="1.0.0",
        lifespan=lifespan,
    )

    api_router = APIRouter(prefix="/api/v1")
        
    api_router.include_router(
        routes_database.router, prefix="/db", tags=["Database"]
    )
    
    api_router.include_router(
        routes_health.router, prefix="/health", tags=["Health Check"]
    )
    
    api_router.include_router(
        routes_auth.router, prefix="/auth", tags=["Authentication Service"]
    )
    
    api_router.include_router(
        routes_rag_engine_wrapper.router,
        prefix="/rag_engine",
        tags=["Rag Engine Wrapper"],
    )

    app.include_router(api_router)
    return app

app = create_app()
