import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler

from app.core.config import Config

config = Config()


class ColorFormatter(logging.Formatter):

    grey = "\x1b[38;20m"
    green = "\x1b[32;1m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(message)s"

    LEVELS = {
        logging.DEBUG: green + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.LEVELS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def get_logger(level=None):
    if not os.path.exists(os.path.dirname(config.log_file)):
        os.makedirs(os.path.dirname(config.log_file))
    if level == 'DEBUG':
        level = logging.DEBUG
    fmt = config.log_format
    log_file = config.log_file
    logger = logging.getLogger()
    logger.setLevel(level or logging.INFO)
    handler = TimedRotatingFileHandler(log_file, when='midnight', backupCount=7)
    formatter = logging.Formatter(fmt, datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(ColorFormatter())
    logger.addHandler(handler)
    logger.addHandler(console)
    return logger
