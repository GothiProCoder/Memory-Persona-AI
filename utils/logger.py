"""
Logging configuration module.

This module provides a centralized logging configuration for the application,
ensuring consistent log formatting and levels across all modules.
"""

import logging
import sys
from config.settings import settings


def get_logger(name: str) -> logging.Logger:
    """
    Get configured logger instance.
    
    Creates a logger with the specified name and configures it with a standard
    stream handler if it doesn't already have handlers. Uses the global
    log level from settings.
    
    Args:
        name (str): The name of the logger, typically `__name__`.
        
    Returns:
        logging.Logger: A configured logger instance.
    """
    logger = logging.getLogger(name)
    
    # Only add handler if not already present to avoid duplicate logs
    if not logger.handlers:
        # Console handler - Write logs to stdout
        handler = logging.StreamHandler(sys.stdout)
        
        # Standard format: Time - Logger Name - Level - Message
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        # Set level based on global configuration
        logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    return logger
