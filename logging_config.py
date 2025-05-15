"""Logging configuration for the application."""
import logging
import sys

# Define a default log level, can be overridden by an environment variable later if needed
LOG_LEVEL = "INFO"

# Basic configuration for the root logger
# This is a simple setup. For more complex needs, consider using a dictionary-based configuration (logging.config.dictConfig)

def setup_logging(log_level: str = LOG_LEVEL):
    """Configures basic logging for the application."""
    # Get the root logger
    logger = logging.getLogger()
    logger.setLevel(log_level.upper())

    # Create a handler for console output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level.upper())

    # Create a formatter and set it for the handler
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)

    # Add the handler to the logger
    # Check if handlers already exist to avoid duplication if this function is called multiple times
    if not logger.handlers:
        logger.addHandler(console_handler)
    
    # Example: You could also add a file handler here if needed
    # file_handler = logging.FileHandler('app.log')
    # file_handler.setFormatter(formatter)
    # logger.addHandler(file_handler)

    # Log a message to indicate logging is configured
    logging.info(f"Logging configured with level: {log_level.upper()}")

# To use in other modules:
# import logging
# logger = logging.getLogger(__name__)
# logger.info("This is an info message from my_module.") 