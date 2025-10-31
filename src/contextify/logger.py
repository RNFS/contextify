import logging
import logging.config



LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s",
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

def setup_logging(verbose: bool = False):
    """
    Configures logging based on verbosity.

    Args:
        verbose: If True, set the root logger level to DEBUG.
    """
    if verbose:
        LOGGING_CONFIG["root"]["level"] = "DEBUG"
    logging.config.dictConfig(LOGGING_CONFIG)

logger = logging.getLogger(__name__)
