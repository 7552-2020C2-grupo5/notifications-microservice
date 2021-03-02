"""Common exceptions."""


class UserTokenDoesNotExist(Exception):
    pass


class ServerTokenError(Exception):
    pass


class UnsetServerToken(Exception):
    pass
