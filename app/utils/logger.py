"""
Centralized logging configuration.

Call `setup_logging()` once, at application startup (see `app/main.py`).
Every other module then just does:

    import logging
    logger = logging.getLogger(__name__)

and inherits the formatting/handlers configured here -- there's no need to
configure logging again anywhere else.
"""

import logging
import sys

from app.config import settings

_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_configured = False


def setup_logging() -> None:
    """Idempotent: safe to call more than once (e.g. across test modules)."""
    global _configured
    if _configured:
        return

    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT))

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers = [handler]

    # Quiet down noisy third-party loggers unless we're explicitly debugging --
    # SQLAlchemy's engine logger in particular echoes every SQL statement.
    if not settings.DEBUG:
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    _configured = True


def get_logger(name: str) -> logging.Logger:
    """Convenience accessor, e.g. `logger = get_logger(__name__)`."""
    return logging.getLogger(name)
