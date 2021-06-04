import logging
import os
import sys
from enum import IntEnum
from logging.handlers import WatchedFileHandler
from multiprocessing import current_process


class LogLevel(IntEnum):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    CRITICAL = logging.CRITICAL
    FATAL = logging.FATAL


class LoggingHandler:
    def __init__(self, log_level: LogLevel):
        self.log_level = log_level
        self.modules_directory = os.path.dirname(__file__)
        self.console_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        self.log_folder = os.path.join(self.modules_directory, "logs/")
        if os.path.exists(self.log_folder) is False:
            os.mkdir(self.log_folder)
        self.log_file = os.path.join(self.modules_directory, "logs/bot_{}.logs".format(str(current_process().ident)))

    def get_console_handler(self):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(self.console_formatter)
        return console_handler

    def get_file_handler(self):
        file_handler = WatchedFileHandler(self.log_file)
        file_handler.setFormatter(self.console_formatter)
        return file_handler

    def get_logger(self, logger_name: str):
        logger = logging.getLogger(logger_name)
        logger.setLevel(self.log_level)
        logger.addHandler(self.get_console_handler())
        logger.addHandler(self.get_file_handler())
        logger.propagate = False
        logger.debug("{0} logger has been initialized.".format(logger_name))
        return logger
