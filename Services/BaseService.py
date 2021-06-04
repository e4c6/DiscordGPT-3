from Implementation.LoggingHandler import LoggingHandler


class BaseService:
    def __init__(self, logger: LoggingHandler):
        self.__logger = logger.get_logger(
            f'{__name__}.{self.__class__.__name__}',
        )
        self.__logger.info(f'{__name__}.{self.__class__.__name__} has been initialized.')
