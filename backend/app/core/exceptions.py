from fastapi import status, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.logger import trace_id_var, get_logger

logger = get_logger(__name__)

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    trace_id = trace_id_var.get("UNKNOWN")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "trace_id": trace_id}
    )
    
async def global_exception_handler(request: Request, exc: Exception):
    trace_id = trace_id_var.get("UNKNOWN")
    
    logger.error(f"Unexpected critical error: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error. Please contact the administrator.",
            "trace_id": trace_id
        }
    )