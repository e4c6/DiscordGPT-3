from Errors import Error


class NotAdminError(Error):
    """Raised when user attempts to use a privileged command"""
    pass
