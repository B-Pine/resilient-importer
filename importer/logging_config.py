"""Logging setup for the importer application."""

import logging
from pathlib import Path

LOGGER_NAME = "importer"
LOG_FORMAT = "%(asctime)s level=%(levelname)s logger=%(name)s %(message)s"


def configure_logging(log_file: Path) -> None:
    """Send the importer's log messages to a file, as an audit trail.

    Only the ``importer`` package's loggers are configured, so log output
    from third-party libraries is not mixed in. Any previous setup is
    removed first, so calling this twice never writes messages twice.

    Args:
        log_file: The file to append log messages to. Its folder is
            created if it does not exist.
    """
    reset_logging()
    log_file.parent.mkdir(parents=True, exist_ok=True)
    handler = logging.FileHandler(log_file, encoding="utf-8")
    handler.setFormatter(logging.Formatter(LOG_FORMAT))

    logger = logging.getLogger(LOGGER_NAME)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def reset_logging() -> None:
    """Remove the importer's log handlers and reset its log level.

    Each handler is closed so its log file is released.
    """
    logger = logging.getLogger(LOGGER_NAME)
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        handler.close()
    logger.setLevel(logging.NOTSET)
