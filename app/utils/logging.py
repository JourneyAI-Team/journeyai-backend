import logging
import sys
from typing import Dict, Any, Optional

from pydantic import BaseModel


class LogConfig(BaseModel):
    """
    Logging configuration for the application
    """
    LOGGER_NAME: str = "journeyai"
    LOG_FORMAT: str = "%(levelprefix)s | %(asctime)s | %(message)s"
    LOG_LEVEL: str = "INFO"

    # Logging config
    version = 1
    disable_existing_loggers = False
    formatters: Dict[str, Dict[str, str]] = {
        "default": {
            "format": LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    }
    handlers: Dict[str, Dict[str, Any]] = {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
        },
    }
    loggers: Dict[str, Dict[str, Any]] = {
        LOGGER_NAME: {"handlers": ["default"], "level": LOG_LEVEL},
    }


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger with the given name
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    logger_name = f"journeyai.{name}" if name else "journeyai"
    return logging.getLogger(logger_name) 