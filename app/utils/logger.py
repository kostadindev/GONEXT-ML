import logging
from logging.handlers import RotatingFileHandler
import os
import sys
from typing import Optional

class Logger:
    """
    Centralized logger class for the application.
    """
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, log_level: str = "INFO", log_file: Optional[str] = None):
        if self._initialized:
            return
            
        self._initialized = True
        
        # Convert string log level to logging constant
        numeric_level = getattr(logging, log_level.upper(), logging.INFO)
        
        # Configure basic logging
        logging.basicConfig(
            level=numeric_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler(sys.stdout)]
        )
        
        # Set up file logging if requested
        if log_file:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            file_handler = RotatingFileHandler(
                log_file, 
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))
            logging.getLogger().addHandler(file_handler)
        
        self.logger = logging.getLogger("app")
    
    def get_logger(self, name: str = None):
        """
        Get a logger instance with the given name.
        
        Args:
            name: The name for the logger
            
        Returns:
            A configured logger instance
        """
        if name:
            return logging.getLogger(f"app.{name}")
        return self.logger

# Create a singleton instance
logger = Logger().get_logger()

def get_logger(name: str = None):
    """
    Get a logger for the specified module.
    
    Args:
        name: The name of the module requesting the logger
        
    Returns:
        A configured logger instance
    """
    return Logger().get_logger(name) 