import logging
from app.config.settings import server_settings

def get_logger(name: str):
    logging.basicConfig(
        level=server_settings.log_level,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
    )
    return logging.getLogger()