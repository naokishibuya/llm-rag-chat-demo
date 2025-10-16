"""
Central logging configuration for the backend.

Usage:
    from logger import get_logger
    LOGGER = get_logger("ask")

Environment variables:
    APP_LOG_LEVEL  -> logging level (DEBUG, INFO, WARNING, ...)
    APP_LOG_FORMAT -> optional custom log format string
    APP_LOG_DATEFMT -> optional date format
"""

import logging
import os

_BASE_LOGGER_NAME = "app"
_LEVEL_NAME = os.getenv("APP_LOG_LEVEL", "INFO").upper()
_LOG_FORMAT = os.getenv(
    "APP_LOG_FORMAT", "%(asctime)s %(name)s %(levelname)s: %(message)s"
)
_DATE_FORMAT = os.getenv("APP_LOG_DATEFMT", "%Y-%m-%d %H:%M:%S")


def _configure_logging() -> None:
    level = getattr(logging, _LEVEL_NAME, logging.INFO)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    if not root_logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(_LOG_FORMAT, _DATE_FORMAT))
        root_logger.addHandler(handler)

    logging.getLogger(_BASE_LOGGER_NAME).setLevel(level)


_configure_logging()


def get_logger(channel: str | None = None) -> logging.Logger:
    """
    Return a logger namespaced under the app.
    """
    name = _BASE_LOGGER_NAME if channel is None else f"{_BASE_LOGGER_NAME}.{channel}"
    return logging.getLogger(name)
