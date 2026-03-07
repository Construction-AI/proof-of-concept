import logging
from pythonjsonlogger.json import JsonFormatter
import contextvars

trace_id_var = contextvars.ContextVar("trace_id", default="SYSTEM")

class TraceIdFilter(logging.Filter):
    def filter(self, record):  # type: ignore
        record.trace_id = trace_id_var.get()
        return True
    
def get_logger(name: str):
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        formatter = JsonFormatter('%(asctime)s %(levelname)s %(name)s %(trace_id)s %(message)s')
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        handler.addFilter(TraceIdFilter())
        
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False 
        
    return logger

def setup_global_logging():
    # Używamy tej samej logiki dla loggerów systemowych (FastAPI/Uvicorn)
    for logger_name in ("uvicorn", "uvicorn.access", "uvicorn.error", "fastapi"):
        get_logger(logger_name)