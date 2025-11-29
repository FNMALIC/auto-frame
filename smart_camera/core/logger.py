"""Logging configuration for Smart Meeting Camera"""

import logging
import sys
from pathlib import Path
from datetime import datetime


def setup_logging(debug: bool = False) -> logging.Logger:
    """
    Setup application logging
    
    Args:
        debug: Enable debug level logging
        
    Returns:
        Logger instance
    """
    # Create logs directory
    log_dir = Path.home() / ".smart_meeting_camera" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Create log file with timestamp
    log_file = log_dir / "app.log"
    
    # Configure logging
    level = logging.DEBUG if debug else logging.INFO
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    
    # Root logger
    logger = logging.getLogger('smart_camera')
    logger.setLevel(level)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    logger.info("=" * 60)
    logger.info("Smart Meeting Camera - Logging initialized")
    logger.info(f"Log file: {log_file}")
    logger.info("=" * 60)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get logger for module
    
    Args:
        name: Module name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(f'smart_camera.{name}')
