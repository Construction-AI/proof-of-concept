import logging
from pythonjsonlogger.json import JsonFormatter
import contextvars

trace_id_var = contextvars.ContextVar("trace_id", default="SYSTEM")

class TraceIdFilter(logging.Filter):
    def filter(self, record): # type: ignore TODO: Specify Type
        record.trace_id = trace_id_var.get()
        return True

def get_logger(name: str):
    logger = logging.getLogger(name=name)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = JsonFormatter(
            '%(asctime)s %(levelname)s %(name)s %(trace_id)s %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.addFilter(TraceIdFilter())
        logger.setLevel(logging.INFO)
        logger.propagate = False
    
    return logger
