#  e4c6 ~ 2021

class ServerError(Exception):
    pass


class NoTokenError(ServerError):
    pass


class AllowanceOverError(ServerError):
    pass


class UserNotMemberError(ServerError):
    pass


class EngineNotAllowedError(ServerError):
    pass
