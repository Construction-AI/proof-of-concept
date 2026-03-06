import logging
from pythonjsonlogger.json import JsonFormatter
import contextvars

trace_id_var = contextvars.ContextVar("trace_id", default="SYSTEM")

class TraceIdFilter(logging.Filter):
    def filter(self, record): # type: ignore TODO: Specify Type
        record.trace_id = trace_id_var.get()
        return True
    
def setup_global_logging():
    formatter = JsonFormatter('%(asctime)s %(levelname)s %(name)s %(trace_id)s %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    handler.addFilter(TraceIdFilter())

    for logger_name in ("uvicorn", "uvicorn.access", "uvicorn.error", "fastapi"):
        sys_logger = logging.getLogger(logger_name)
        sys_logger.handlers = [handler]
        sys_logger.propagate = False

def get_logger(name: str):
    logger = logging.getLogger(name)
    if not logger.handlers:
        pass 
    return logger
