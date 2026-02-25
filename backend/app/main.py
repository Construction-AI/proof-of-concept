from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from app.modules.auth.router import router as auth_router
from app.modules.projects.router import router as projects_router
from app.modules.documents.router import router as documents_router
from app.modules.health.router import router as health_router
from app.modules.rag.router import router as rag_router
from app.modules.templates.router import router as templates_router
from app.modules.generator.router import router as generator_router

from app.db.session import engine
from app.db.base import Base

from app.core.config import settings

Base.metadata.create_all(bind=engine)

# from contextlib import asynccontextmanager

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     yield

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.SERVICE_NAME,
        description="Document ingestion, indexing and querying API using LlamaIndex and Qdrant.",
        version=settings.APP_VERSION,
        # lifespan=lifespan,
    )

    api_router = APIRouter(prefix="/api/v1")
    
    api_router.include_router(auth_router, prefix="/auth", tags=["Authentication Section"])
    api_router.include_router(projects_router, prefix="/projects", tags=["Projects Section"])
    api_router.include_router(documents_router, prefix="/documents", tags=["Documents Section"])
    api_router.include_router(rag_router, prefix="/rag", tags=["RAG Section"])
    api_router.include_router(health_router, prefix="/health", tags=["Health Section"])
    api_router.include_router(templates_router, prefix="/templates", tags=["Templates Section"])
    api_router.include_router(generator_router, prefix="/generator", tags=["Generator Section"])
    
    app.include_router(api_router)
    
    return app

app = create_app()


origins = [
    "http://localhost:5173",     # Twój lokalny frontend Vite
    "http://127.0.0.1:5173",     # Alternatywny zapis localhosta
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # Zezwalamy na te adresy
    allow_credentials=True,      # Zezwalamy na przesyłanie ciasteczek/autoryzacji
    allow_methods=["*"],         # Zezwalamy na wszystkie metody (GET, POST, PUT, DELETE)
    allow_headers=["*"],         # Zezwalamy na wszystkie nagłówki (w tym nasz Authorization: Bearer)
)
