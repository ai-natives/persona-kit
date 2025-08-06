"""Logging configuration for PersonaKit."""
import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any

from .config import settings


class JSONFormatter(logging.Formatter):
    """JSON log formatter."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_obj: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add extra fields if present
        if hasattr(record, "correlation_id"):
            log_obj["correlation_id"] = record.correlation_id

        # Add exception info if present
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_obj)


def setup_logging() -> None:
    """Configure application logging."""
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.log_level.upper()))

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)

    # Set formatter based on environment
    if settings.log_format == "json":
        console_handler.setFormatter(JSONFormatter())
    else:
        console_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
        )

    root_logger.addHandler(console_handler)

    # Set specific log levels for noisy libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
