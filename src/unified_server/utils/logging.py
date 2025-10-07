"""
Logging utilities for the unified server.
"""

import logging
import sys
from typing import Optional


def setup_logging(level: str = "INFO", format_string: Optional[str] = None) -> logging.Logger:
    """
    Setup logging configuration
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_string: Custom format string for log messages
    
    Returns:
        Configured logger instance
    """
    # Validate and sanitize log level
    valid_levels = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}
    safe_level = level.upper() if level.upper() in valid_levels else 'INFO'
    
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    else:
        # Sanitize format string to prevent injection
        format_string = format_string.replace('\n', '').replace('\r', '')[:200]
    
    try:
        # Use only safe, predefined configurations
        logging.basicConfig(
            level=getattr(logging, safe_level, logging.INFO),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Fixed format
            datefmt='%Y-%m-%d %H:%M:%S',
            handlers=[
                logging.StreamHandler(sys.stdout)
            ],
            force=True  # Override existing configuration
        )
    except Exception:
        # Fallback to minimal safe configuration
        logging.basicConfig(
            level=logging.INFO,
            format='%(levelname)s - %(message)s',
            force=True
        )
    
    return logging.getLogger("unified_server")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance
    
    Args:
        name: Logger name
    
    Returns:
        Logger instance
    """
    # Sanitize logger name to prevent injection
    safe_name = name.replace('\n', '').replace('\r', '').replace('..', '')[:50]
    return logging.getLogger(f"unified_server.{safe_name}")