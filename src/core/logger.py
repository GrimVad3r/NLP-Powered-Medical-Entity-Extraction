"""
Structured logging with rotation and JSON formatting.

BRANCH-1: Core Utilities
Author: Boris (Claude Code)
"""

import json
import logging
import logging.handlers
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from src.core.config import get_settings


class JSONFormatter(logging.Formatter):
    """JSON log formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        if hasattr(record, "extra"):
            log_data.update(record.extra)

        return json.dumps(log_data)


class StandardFormatter(logging.Formatter):
    """Standard text log formatter."""

    FORMAT = (
        "%(asctime)s - %(name)s - %(levelname)s - "
        "%(module)s:%(funcName)s:%(lineno)d - %(message)s"
    )

    def __init__(self):
        """Initialize formatter."""
        super().__init__(self.FORMAT, datefmt="%Y-%m-%d %H:%M:%S")


def setup_logger(
    name: str,
    level: Optional[str] = None,
    log_file: Optional[Path] = None,
) -> logging.Logger:
    """
    Setup a logger with console and file handlers.

    Args:
        name: Logger name
        level: Logging level (defaults to settings)
        log_file: Optional log file path

    Returns:
        logging.Logger: Configured logger instance

    Example:
        >>> logger = setup_logger(__name__)
        >>> logger.info("Starting application", extra={"user_id": 123})
    """
    settings = get_settings()
    logger = logging.getLogger(name)

    # Set level
    log_level = (level or settings.log_level).upper()
    logger.setLevel(log_level)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    # File handler with rotation
    if log_file or settings.log_dir:
        log_dir = Path(log_file.parent if log_file else settings.log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)

        log_path = log_file or log_dir / f"{name.replace('.', '_')}.log"

        file_handler = logging.handlers.RotatingFileHandler(
            log_path,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
        )
        file_handler.setLevel(log_level)

        # Apply formatter
        formatter = (
            JSONFormatter()
            if settings.log_format.lower() == "json"
            else StandardFormatter()
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Apply formatter to console
    formatter = (
        JSONFormatter()
        if settings.log_format.lower() == "json"
        else StandardFormatter()
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Prevent propagation
    logger.propagate = False

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get or create a logger.

    Args:
        name: Logger name (usually __name__)

    Returns:
        logging.Logger: Logger instance

    Example:
        >>> from src.core.logger import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("Application started")
    """
    return setup_logger(name)


class LogContext:
    """Context manager for adding context to logs."""

    def __init__(self, logger: logging.Logger, **context):
        """
        Initialize context manager.

        Args:
            logger: Logger instance
            **context: Context key-value pairs
        """
        self.logger = logger
        self.context = context

    def __enter__(self):
        """Enter context."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context."""
        if exc_type:
            self.logger.error(
                f"Exception in context: {exc_val}",
                extra=self.context,
            )
            return False
        return True

    def log(self, level: str, message: str, **kwargs):
        """Log message with context."""
        extra = {**self.context, **kwargs}
        getattr(self.logger, level.lower())(message, extra=extra)


# Module-level logger
logger = get_logger(__name__)