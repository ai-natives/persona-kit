"""Logging configuration for PersonaKit Workbench."""
import json
import logging
import os
import sys
from datetime import UTC, datetime
from typing import Any


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
            "service": "personakit-workbench",
        }

        # Add exception info if present
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_obj)


def setup_logging(service_name: str = "workbench") -> None:
    """Configure application logging.
    
    Args:
        service_name: Name of the service for log identification
    """
    # Get root logger
    root_logger = logging.getLogger()
    
    # Set log level from env or default to INFO
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    root_logger.setLevel(getattr(logging, log_level))

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create handlers
    handlers = []
    
    # Always add console handler
    console_handler = logging.StreamHandler(sys.stdout)
    handlers.append(console_handler)
    
    # Add file handler if LOG_FILE env var is set
    log_file = os.getenv("LOG_FILE")
    if log_file:
        # Ensure directory exists
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        handlers.append(file_handler)

    # Set formatter based on environment
    log_format = os.getenv("LOG_FORMAT", "text")
    if log_format == "json":
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            f"%(asctime)s - [{service_name.upper()}] - %(name)s - %(levelname)s - %(message)s"
        )
    
    # Apply formatter to all handlers
    for handler in handlers:
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)

    # Set specific log levels for noisy libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)