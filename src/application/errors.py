class ApplicationError(Exception):
    """Base class for errors exposed by the application boundary."""


class ActivitiesNotFoundError(ApplicationError):
    """Raised when a use case requires activities but none are available."""


class ExternalServiceError(ApplicationError):
    """Base class for failures reported by an external service adapter."""


class RateLimitExceededError(ExternalServiceError):
    """Raised when an external service rejects a request due to its rate limit."""


class InactiveApplicationError(ExternalServiceError):
    """Raised when Strava has marked the configured API application inactive."""


class UnauthorizedError(ExternalServiceError):
    """Raised when an external service rejects the supplied credentials."""


class TokenError(ApplicationError):
    """Base class for OAuth token acquisition failures."""


class TokenStorageError(TokenError):
    """Raised when the configured token store cannot read or write tokens."""
