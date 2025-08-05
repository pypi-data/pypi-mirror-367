"""
Logger configuration for the cache middleware.

This module provides logger setup using loguru, which replaces
the standard Python logging module for better performance and
ease of use. It's specifically named logger_config.py to avoid
circular import issues with the stdlib logging module.
"""

from loguru import logger


def configure_logger():
    """
    Configure the logger for the application.
    
    This function sets up the loguru logger with default settings.
    It can be extended to add custom log handlers, formatters,
    and output destinations.
    
    Examples
    --------
    >>> configure_logger()
    >>> logger.info("Application started")
    
    Notes
    -----
    Common configuration options that can be added:
    - File rotation: logger.add("app.log", rotation="1 MB", level="INFO")
    - Console output: logger.add(sys.stderr, level="DEBUG")
    - JSON formatting: logger.add("app.json", serialize=True)
    """
    # Default configuration - can be extended as needed
    # logger.add("cache_middleware.log", rotation="1 MB", level="INFO")
    # logger.add(sys.stderr, level="DEBUG")
    pass


# Export the logger for use in other modules
__all__ = ["logger", "configure_logger"]
