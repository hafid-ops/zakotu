import logging
import sys
from logging.handlers import TimedRotatingFileHandler

def setup_logger():
    logger = logging.getLogger("ZAKUTO_Logger")
    logger.setLevel(logging.INFO)

    # Prevent duplicate logs if logger is already configured
    if logger.hasHandlers():
        logger.handlers.clear()

    # Formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Console Handler
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.INFO)
    stdout_handler.setFormatter(formatter)
    logger.addHandler(stdout_handler)

    # File Handler
    file_handler = TimedRotatingFileHandler('logs/ZAKUTO.log', when='midnight', interval=1, backupCount=7)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

# Global logger instance
logger = setup_logger()
