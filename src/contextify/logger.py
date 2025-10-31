"""
Logging configuration for contextify.

This module provides a centralized logging setup using Python's built-in
logging module with a dictionary-based configuration for flexibility and
structured output suitable for both development and production environments.
"""

import logging
import logging.config
from typing import Dict, Any

# Logging configuration dictionary
LOGGING_CONFIG: Dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "verbose": {
            "format": (
                "[%(asctime)s] [%(levelname)s] [%(name)s:%(funcName)s:%(lineno)d] - "
                "%(message)s"
            ),
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "stream": "ext://sys.stdout",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console"],
    },
}


def setup_logging(verbose: bool = False) -> None:
    """
    Configure logging based on verbosity level.

    When verbose mode is enabled, the logger will output DEBUG level messages
    with more detailed information including function names and line numbers.
    Otherwise, INFO level messages are output with a standard format.

    Args:
        verbose (bool): If True, set root logger level to DEBUG and use verbose
                       formatter. Defaults to False.

    Returns:
        None
    """
    config = LOGGING_CONFIG.copy()
    if verbose:
        config["root"]["level"] = "DEBUG"
        config["handlers"]["console"]["formatter"] = "verbose"
    logging.config.dictConfig(config)


def get_logger(name: str) -> logging.Logger:
    """
    Get a module-specific logger instance.

    Args:
        name (str): The name of the logger, typically __name__ from the calling module.

    Returns:
        logging.Logger: A configured logger instance.
    """
    return logging.getLogger(name)
