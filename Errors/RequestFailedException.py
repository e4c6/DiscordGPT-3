from string import Template

from Errors import *
from Errors.OpenAIError import OpenAIError
from Errors.TokenExhaustedError import TokenExhaustedError
from Errors.TokenInvalidError import TokenInvalidError


class RequestFailedException(Error):
    def __init__(self, status_code: int):
        self.status_code = status_code
        self.try_handle()

    def __str__(self):
        return repr(self.status_code)

    def try_handle(self):
        if self.status_code == 429:
            raise TokenExhaustedError
        elif self.status_code == 400:
            raise TokenInvalidError
        elif self.status_code == 500:
            raise OpenAIError
        raise NotImplementedError(
            Template("$input status code has no exception handler.").substitute(input=self.status_code))
