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


def log(logger_func, message, *args):
    log_message = f"{message}: {' '.join(args)}" if args else message
    logger_func(log_message)
