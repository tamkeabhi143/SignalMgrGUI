import os
import logging
import logging.handlers
import sys
from datetime import datetime

def setup_logging(app_name="SignalMgrGUI", log_level=logging.INFO):
    """Configure application logging
    
    This sets up:
    1. Console logging for command line usage
    2. File logging for persistent records
    3. Special error logging for exceptions
    
    Args:
        app_name: Name of the application for log file names
        log_level: Default logging level (DEBUG, INFO, WARNING, ERROR)
    
    Returns:
        Logger object for use throughout the application
    """
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    # Create a logger
    logger = logging.getLogger(app_name)
    logger.setLevel(log_level)
    
    # If handlers already exist, don't add more
    if logger.handlers:
        return logger
    
    # Create a formatter with timestamp
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Add console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Add file handler with date-based filename
    today = datetime.now().strftime('%Y-%m-%d')
    log_file = os.path.join(log_dir, f"{app_name}_{today}.log")
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=10485760, backupCount=5
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Add special error handler for higher-level errors
    error_file = os.path.join(log_dir, f"{app_name}_errors.log")
    error_handler = logging.handlers.RotatingFileHandler(
        error_file, maxBytes=10485760, backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)
    
    logger.info(f"Logging initialized for {app_name}")
    return logger

def log_uncaught_exceptions(logger):
    """
    Set up hook to catch and log unhandled exceptions
    
    Args:
        logger: The logger to use for exception logging
    """
    def exception_handler(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            # Don't log keyboard interrupt
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        # Log the exception
        logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
        
        # Call the default handler which prints to stderr
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
    
    sys.excepthook = exception_handler
