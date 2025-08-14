import logging
from vkbottle.modules import ColorFormatter


def get_logger(name: str, level: str = logging.INFO) -> logging.Logger:
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(ColorFormatter())

    logger = logging.getLogger(name)
    logger.addHandler(stream_handler)
    logger.setLevel(level)

    return logger


def disable_loggers(logger: logging.Logger, *names):
    for name, _logger in logging.root.manager.loggerDict.items():
        if name.startswith(names) and isinstance(_logger, logging.Logger):
            logger.info(f"Disabled logger {name}")
            _logger.setLevel(logging.CRITICAL)
