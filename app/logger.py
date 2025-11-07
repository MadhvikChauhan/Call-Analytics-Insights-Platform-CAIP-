
"""Centralized logging configuration for CAIP.

Provides `get_logger` which returns a module-level logger configured to log
to both console and a rotating file handler under `logs/`.
"""
import logging
import os
from logging.handlers import RotatingFileHandler
from .config import settings

LOG_DIR = os.path.join(os.getcwd(), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "app.log")

def get_logger(name: str = __name__) -> logging.Logger:
    """Create and return a configured logger.

    Args:
        name: Logger name (usually __name__ from the calling module).

    Returns:
        Configured `logging.Logger` instance.
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger  # already configured

    logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    ch_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(ch_formatter)

    # Rotating file handler
    fh = RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount=3)
    fh.setLevel(logging.DEBUG)
    fh_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(fh_formatter)

    logger.addHandler(ch)
    logger.addHandler(fh)
    return logger
