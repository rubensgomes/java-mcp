import logging

# Configure logging for this module
logger = logging.getLogger(__name__)

def configure_logging(level: str = "INFO") -> None:
    """
    Configure logging for the application.

    Args:
        level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')

    # Configure logging with detailed format
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        force=True  # Override any existing configuration
    )
