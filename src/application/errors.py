class ApplicationError(Exception):
    """Base class for errors exposed by the application boundary."""


class ActivitiesNotFoundError(ApplicationError):
    """Raised when a use case requires activities but none are available."""


class ExternalServiceError(ApplicationError):
    """Base class for failures reported by an external service adapter."""


class ExternalServiceUnavailableError(ExternalServiceError):
    """Raised when an external service cannot be reached after retries."""


class ExternalServiceResponseError(ExternalServiceError):
    """Raised for an unexpected HTTP response from an external service."""

    def __init__(self, message: str, *, status_code: int) -> None:
        super().__init__(message)
        self.status_code = status_code


class InvalidExternalDataError(ExternalServiceError):
    """Raised when an external service returns data that violates its contract."""


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
