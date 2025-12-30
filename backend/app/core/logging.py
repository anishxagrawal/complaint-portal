# app/core/logging.py
"""
Logging configuration for the Complaint Portal.

Sets up:
- File logging (logs/app.log)
- Console logging (with colors)
- Rotating file handler (10MB max, 5 backups)
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler


def setup_logging(log_level: str = "INFO") -> None:
    """
    Configure application logging.
    
    Creates:
    - Console handler (colored, INFO+)
    - File handler (all levels, rotated)
    
    Args:
        log_level: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Get root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers (avoid duplicates)
    logger.handlers.clear()
    
    # ==========================================
    # Console Handler (with colors)
    # ==========================================
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # Format: [2024-01-15 10:30:45] INFO - app.routers.complaints - Complaint created
    console_format = logging.Formatter(
        fmt="[%(asctime)s] %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # ==========================================
    # File Handler (rotating, 10MB max)
    # ==========================================
    
    file_handler = RotatingFileHandler(
        filename=log_dir / "app.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,               # Keep 5 old files
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)  # Log everything to file
    
    # More detailed format for file logs
    file_format = logging.Formatter(
        fmt="[%(asctime)s] %(levelname)-8s | %(name)-30s | %(funcName)-20s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)
    
    # ==========================================
    # Error File Handler (errors only)
    # ==========================================
    
    error_handler = RotatingFileHandler(
        filename=log_dir / "errors.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    error_handler.setLevel(logging.ERROR)  # Only errors and critical
    error_handler.setFormatter(file_format)
    logger.addHandler(error_handler)
    
    # ==========================================
    # Suppress noisy third-party loggers
    # ==========================================
    
    # Reduce SQLAlchemy verbosity
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
    
    # Reduce uvicorn verbosity
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    
    logger.info("✅ Logging configured successfully")
    logger.info(f"📂 Log files: {log_dir.absolute()}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.
    
    Usage:
        from app.core.logging import get_logger
        logger = get_logger(__name__)
        logger.info("Something happened")
    
    Args:
        name: Usually __name__ (module name)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)