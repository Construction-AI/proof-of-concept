from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

# Create main API router
router = APIRouter(prefix="/api")

# Health check endpoint
@router.get("/health", response_class=PlainTextResponse, tags=["health"])
async def health_check():
    return "ok"

# Import and include route modules
from app.api.routes import documents_router, indexes_router

# Include the routers
router.include_router(documents_router)
router.include_router(indexes_router)