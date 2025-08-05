import sys
import logging


def setup_logging(enable_logging: bool) -> None:
    """
    Set up logging configuration.
    
    Args:
        enable_logging (bool): Whether to enable verbose logging.
    """
    if enable_logging:
        log_format = '[%(levelname)s] %(message)s'
        handlers = [
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('image_archive_viewer.log', mode='w', encoding='utf-8')
        ]
        logging.basicConfig(level=logging.INFO, format=log_format, handlers=handlers)
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        logger.info('Logging enabled (console and file)')
    else:
        logging.basicConfig(level=logging.CRITICAL)  # Only log critical errors
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.CRITICAL)