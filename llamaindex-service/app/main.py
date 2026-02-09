from fastapi import FastAPI, APIRouter

from app.modules.auth.router import router as auth_router
from app.db.session import engine
from app.db.base import Base
from app.modules.auth import models as auth_models

Base.metadata.create_all(bind=engine)

from contextlib import asynccontextmanager

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     yield

def create_app() -> FastAPI:
    app = FastAPI(
        title="LlamaIndex Service",
        description="Document ingestion, indexing and querying API using LlamaIndex and Qdrant.",
        version="1.0.0",
        # lifespan=lifespan,
    )

    api_router = APIRouter(prefix="/api/v1")
    api_router.include_router(auth_router, prefix="/auth")
    app.include_router(api_router)
    
    return app

app = create_app()
