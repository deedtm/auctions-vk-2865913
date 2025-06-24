import logging
from vkbottle.modules import ColorFormatter


def get_logger(name: str, level: str = logging.INFO) -> logging.Logger:
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(ColorFormatter())

    logger = logging.getLogger(name)
    logger.addHandler(stream_handler)
    logger.setLevel(level)

    return logger
