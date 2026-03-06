import logging
from pythonjsonlogger.json import JsonFormatter

def get_logger(name: str):
    logger = logging.getLogger(name=name)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = JsonFormatter(
            '%(asctime)s %(levelname)s %(name)s %(message)s %(module)s %(funcName)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger
