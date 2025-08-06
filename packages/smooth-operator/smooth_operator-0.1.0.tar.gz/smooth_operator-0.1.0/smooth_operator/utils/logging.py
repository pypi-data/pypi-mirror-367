# smooth_operator/utils/logging.py
import logging
import structlog
import sys
from typing import Optional


def configure_logging(
    level: str = "INFO",
    console: bool = True,
    file_path: Optional[str] = None,
    json_format: bool = False,
):
    """Configure structured logging for the application."""
    log_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
    ]

    if json_format:
        log_processors.append(structlog.processors.JSONRenderer())
    else:
        log_processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=log_processors,
        wrapper_class=structlog.make_filtering_bound_logger(getattr(logging, level.upper())),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory() if console and not file_path else structlog.stdlib.LoggerFactory(),
    )

    if file_path:
        # Configure file logging if a path is provided
        file_handler = logging.FileHandler(file_path)
        # The formatter is not strictly needed for structlog with stdlib,
        # but can be useful if non-structlog logs are also being captured.
        formatter = logging.Formatter("%(message)s")
        file_handler.setFormatter(formatter)

        # Get the root logger and add the file handler
        root_logger = logging.getLogger()
        root_logger.addHandler(file_handler)
        root_logger.setLevel(getattr(logging, level.upper()))

def get_logger(name: Optional[str] = None) -> any:
    """Get a structured logger instance."""
    return structlog.get_logger(name)
