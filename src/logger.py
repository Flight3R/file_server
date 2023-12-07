import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('http_server.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def log(logger_func, message, *args, **kwargs):
    log_message = f"{message}: {' '.join(args)}"
    logger_func(log_message)

# logger.debug('This is a debug message')
# logger.info('This is an info message')
# logger.warning('This is a warning message')
# logger.error('This is an error message')
# logger.critical('This is a critical message')
