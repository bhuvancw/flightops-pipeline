import logging
from src.config import LOG_DIR

def get_logger(name):
    LOG_DIR.mkdir(exist_ok=True)
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    fmt = logging.Formatter('%(asctime)s | %(levelname)s | %(name)s | %(message)s')

    file_handler = logging.FileHandler(LOG_DIR / 'pipeline.log')
    file_handler.setFormatter(fmt)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(fmt)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger

