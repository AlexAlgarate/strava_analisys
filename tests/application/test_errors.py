import pytest

from src.application.errors import (
    ActivitiesNotFoundError,
    ApplicationError,
    ExternalServiceError,
    InactiveApplicationError,
    RateLimitExceededError,
    TokenError,
    TokenStorageError,
    UnauthorizedError,
)


@pytest.mark.parametrize(
    ("error", "base"),
    [
        (ActivitiesNotFoundError("empty"), ApplicationError),
        (ExternalServiceError("offline"), ApplicationError),
        (InactiveApplicationError("inactive"), ExternalServiceError),
        (RateLimitExceededError("limited"), ExternalServiceError),
        (UnauthorizedError("unauthorized"), ExternalServiceError),
        (TokenError("token"), ApplicationError),
        (TokenStorageError("storage"), TokenError),
    ],
)
def test_application_error_hierarchy(error: Exception, base: type[Exception]) -> None:
    assert isinstance(error, base)
