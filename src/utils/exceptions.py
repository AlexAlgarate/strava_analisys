class NotActivitiesError(Exception):
    pass


class TooManyRequestError(Exception):
    pass


class TokenError(Exception):
    pass


class TokenStorageError(TokenError):
    pass


class UnauthorizedError(Exception):
    pass
