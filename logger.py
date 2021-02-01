import logging
from logging.handlers import WatchedFileHandler
import os
import sys
from multiprocessing import current_process

modules_directory = os.path.dirname(__file__)
console_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

LOG_FOLDER = os.path.join(modules_directory, "logs/")
if os.path.exists(LOG_FOLDER) is False:
    os.mkdir(LOG_FOLDER)
LOG_FILE = os.path.join(modules_directory, "logs/bot_{}.logs".format(str(current_process().ident)))


def get_console_handler():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    return console_handler


def get_file_handler():
    file_handler = WatchedFileHandler(LOG_FILE)
    file_handler.setFormatter(console_formatter)
    return file_handler


def get_logger(logger_name):  # , identifiers
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(get_console_handler())
    logger.addHandler(get_file_handler())
    # logger = logging.LoggerAdapter(logger, identifiers)
    logger.propagate = False
    return logger
