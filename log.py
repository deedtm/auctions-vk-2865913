import logging
from vkbottle.modules import ColorFormatter


def get_logger(name: str, *args) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    logger.handlers.clear()
    
    file_formatter = logging.Formatter('%(levelname)-8s | %(asctime)s | %(name)s:%(funcName)s:%(lineno)d > %(message)s')
    
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(ColorFormatter())
    stream_handler.setLevel(logging.INFO)
    logger.addHandler(stream_handler)
    
    warning_handler = logging.FileHandler('warnings.log', encoding='utf-8')
    warning_handler.setFormatter(file_formatter)
    warning_handler.setLevel(logging.WARNING)
    logger.addHandler(warning_handler)
    
    debug_handler = logging.FileHandler('debug.log', encoding='utf-8')
    debug_handler.setFormatter(file_formatter)
    debug_handler.setLevel(logging.DEBUG)
    logger.addHandler(debug_handler)

    return logger


def disable_loggers(logger: logging.Logger, *names):
    for name, _logger in logging.root.manager.loggerDict.items():
        if name.startswith(names) and isinstance(_logger, logging.Logger):
            logger.info(f"Disabled logger {name}")
            _logger.setLevel(logging.CRITICAL)