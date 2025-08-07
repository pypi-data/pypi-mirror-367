import logging
import logging.config

from snakestack.config import settings

DEFAULT_HANDLERS = {
    "console": {
        "class": "logging.StreamHandler",
        "formatter": settings.snakestack_default_formatter,
    }
}


DEFAULT_FORMATTERS = {
    "default": {
        "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    },
    "with_request_id": {
        "format": (
            "%(asctime)s [%(levelname)s] [req_id=%(request_id)s] "
            "%(name)s: %(message)s"
        )
    }
}

DEFAULT_LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": DEFAULT_FORMATTERS,
    "handlers": DEFAULT_HANDLERS,
    "root": {
        "level": settings.snakestack_log_level,
        "handlers": ["console"]
    }
}


def setup_logging() -> None:
    logging.config.dictConfig(DEFAULT_LOGGING_CONFIG)
