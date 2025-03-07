import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import app configurations
from app.core.config import settings
from app.core.logging import logger
from app.api import router as api_router

# Create the FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOW_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Set app state variables for directory paths
app.state.documents_dir = settings.DOCUMENTS_DIR
app.state.indexes_dir = settings.INDEXES_DIR

# Include API router
app.include_router(api_router)

@app.get("/")
async def root():
    return {
        "message": settings.API_TITLE,
        "docs": "/docs",
        "status": "operational"
    }

if __name__ == "__main__":
    logger.info(f"Starting server on {settings.HOST}:{settings.PORT}")
    logger.info(f"Documents directory: {settings.DOCUMENTS_DIR}")
    logger.info(f"Logs directory: {settings.LOG_DIR}")
    
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)