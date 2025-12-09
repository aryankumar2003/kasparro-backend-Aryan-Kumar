import logging
import sys
from core.config import settings

def setup_logging():
    """
    Configure logging for the application.
    """
    logger = logging.getLogger()
    logger.setLevel(settings.LOG_LEVEL)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    
    
    
    

    logging.info("Logging initialized")
