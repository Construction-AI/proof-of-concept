import logging
import sys

def configure_logging(level="INFO"):
    """Konfiguruje globalny logger aplikacji."""

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(level)
    root.addHandler(handler)

def get_logger(name: str):
    return logging.getLogger(name)
