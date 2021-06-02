from functools import wraps

from Errors.CreditExhaustedError import CreditExhaustedError
from Errors.EmptyPromptError import EmptyPromptError
from Errors.NotAdminError import NotAdminError
from Errors.OpenAIError import OpenAIError
from Errors.TokenExhaustedError import TokenExhaustedError
from Errors.TokenInvalidError import TokenInvalidError


def try_catch_log(method):
    @wraps(method)
    def _impl(self, *method_args, **method_kwargs):
        try:
            return method(self, *method_args, **method_kwargs)
        except Exception as e:
            self.__logger.error("{} threw an exception: {}".format(method.__name__, e))
            return e

    return _impl


def check_setup(method):
    @wraps(method)
    async def _impl(self, *method_args, **method_kwargs):
        if await self.check_server_token(method_args[0]):
            try:
                return await method(self, *method_args, **method_kwargs)
            except TokenExhaustedError:
                return await self.token_exhausted(method_args[0])
            except TokenInvalidError:
                return await self.token_invalid(method_args[0])
            except EmptyPromptError:
                return await self.empty_warning(method_args[0])
            except CreditExhaustedError:
                return await self.credit_warning(method_args[0])
            except OpenAIError:
                return await self.openai_down_warning(method_args[0])
            except NotAdminError:
                return await self.not_admin_warning(method_args[0])
        return await self.prompt_setup(method_args[0])

    return _impl
