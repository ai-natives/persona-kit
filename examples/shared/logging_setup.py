"""Shared logging configuration for PersonaKit services."""
import logging
import os
import sys
from typing import Optional


def setup_service_logging(service_name: str, log_level: str = "INFO") -> logging.Logger:
    """
    Configure logging for a PersonaKit service.
    
    Args:
        service_name: Name of the service (e.g., "agno-coaching", "career-navigator")
        log_level: Logging level (default: INFO)
        
    Returns:
        Configured logger instance
        
    Environment Variables:
        LOG_FILE: If set, logs will also be written to this file
        LOG_LEVEL: Override the default log level
    """
    # Override log level from env if set
    log_level = os.getenv("LOG_LEVEL", log_level).upper()
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    
    # Add file handler if LOG_FILE is set
    log_file = os.getenv("LOG_FILE")
    if log_file:
        # Ensure directory exists
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
            
        # Create file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        logging.getLogger().addHandler(file_handler)
    
    # Return logger for the service
    return logging.getLogger(service_name)