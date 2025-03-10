from fastapi import APIRouter

# Create main API router
router = APIRouter(prefix="/api")

# Health check endpoint
@router.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok"}

# Import and include route modules
from app.api.routes import documents_router, indexes_router

# Include the routers
router.include_router(documents_router)
router.include_router(indexes_router)