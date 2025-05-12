import logging
from logging.handlers import RotatingFileHandler
import os
from typing import Optional

def setup_logger(name: str, config: Optional[Dict] = None) -> logging.Logger:
    """Configure production-ready logger"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Console handler
    ch = logging.StreamHandler()
    ch.setFormatter(_get_formatter())
    logger.addHandler(ch)
    
    # File handler
    if config:
        os.makedirs('logs', exist_ok=True)
        fh = RotatingFileHandler(
            config['file'],
            maxBytes=config['max_size']*1024*1024,
            backupCount=3
        )
        fh.setFormatter(_get_formatter())
        logger.addHandler(fh)
        
    return logger

def _get_formatter():
    return logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )