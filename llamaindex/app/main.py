# app/main.py - Updated with absolute paths
import logging
import uvicorn
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import directories

# Get the project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Configure directories
LOG_DIR = os.path.join(PROJECT_ROOT, "data", "logs")
DOCUMENTS_DIR = os.path.join(PROJECT_ROOT, "data", "documents")
INDEXES_DIR = os.path.join(PROJECT_ROOT, "data", "indexes")

# Create necessary directories
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(DOCUMENTS_DIR, exist_ok=True)
os.makedirs(INDEXES_DIR, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(LOG_DIR, "app.log"), mode="a")
    ]
)
logger = logging.getLogger(__name__)

# Create the FastAPI app
app = FastAPI(
    title="Document Processing API",
    description="API for processing and querying documents using LlamaIndex and Qdrant",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pass the correct documents directory to the router
app.include_router(directories.router)

# Make the directories available to other modules
app.state.documents_dir = DOCUMENTS_DIR
app.state.indexes_dir = INDEXES_DIR

@app.get("/")
async def root():
    return {
        "message": "Document Processing API",
        "docs": "/docs",
        "status": "operational"
    }

if __name__ == "__main__":
    # Get configuration from environment variables
    PORT = int(os.getenv("PORT", "8000"))
    HOST = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"Starting server on {HOST}:{PORT}")
    logger.info(f"Documents directory: {DOCUMENTS_DIR}")
    logger.info(f"Logs directory: {LOG_DIR}")
    
    uvicorn.run("app.main:app", host=HOST, port=PORT, reload=True)