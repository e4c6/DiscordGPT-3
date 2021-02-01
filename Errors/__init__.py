class Error(Exception):
    """Base class for other exceptions"""
    pass


class TokenExhaustedError(Error):
    """Raised when api returns 429"""
    pass


class TokenInvalidError(Error):
    """Raised when api returns 400"""
    pass


class OpenAIError(Error):
    """Raised when api returns 500"""
    pass


class EmptyPromptError(Error):
    """Raised when user gives an empty input"""
    pass


class CreditExhaustedError(Error):
    """Raised when user attempts to use more credit than allowed"""
    pass
