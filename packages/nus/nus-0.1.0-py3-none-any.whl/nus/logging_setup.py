"""Set up logging for the nus application.

This module configures logging for the nus application, ensuring that log handlers
are only added once to prevent duplicate log entries if the module is imported
multiple times.

Attributes:
    logger (logging.Logger): The main logger for the nus application.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler

from nus.config import DEFAULT_USER_HOME_CACHE_PATH, log_file_path


def setup_logger() -> logging.Logger:
    """Set up and return the main logger for the nus application.

    Ensures that handlers are only added once to avoid duplicate log entries
    if this module is imported multiple times.

    Returns:
        logging.Logger: Configured logger for the nus application.
    """
    logger = logging.getLogger("nus")
    logger.setLevel(logging.INFO)

    # Only add handlers if they haven't been added yet
    if not logger.handlers:
        # Ensure the log file exists
        DEFAULT_USER_HOME_CACHE_PATH.mkdir(parents=True, exist_ok=True)

        # Create a file handler that logs all messages
        file_handler = RotatingFileHandler(
            log_file_path, maxBytes=10 * 1024 * 1024, backupCount=5
        )
        file_handler.setLevel(logging.INFO)

        # Create a console handler for errors only
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(logging.ERROR)

        # Create a formatter and set it for both handlers
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add the handlers to the logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger


logger: logging.Logger = setup_logger()
"""The main logger for the nus application."""
