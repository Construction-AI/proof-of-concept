import logging
import os
from app.core.config import settings

def setup_logging():
    """Configure logging for the application"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(os.path.join(settings.LOG_DIR, "app.log"), mode="a")
        ]
    )
    
    # Reduce noise from some libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    
    logger = logging.getLogger("app")
    logger.info("Logging configured successfully")
    return logger

# Initialize logger
logger = setup_logging()