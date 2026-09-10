import pytest

from src.application.errors import (
    ApplicationError,
    ExternalServiceError,
    ExternalServiceResponseError,
    ExternalServiceUnavailableError,
    InactiveApplicationError,
    InvalidExternalDataError,
    RateLimitExceededError,
    TokenError,
    TokenStorageError,
    UnauthorizedError,
)


@pytest.mark.parametrize(
    ("error", "base"),
    [
        (ExternalServiceError("offline"), ApplicationError),
        (ExternalServiceUnavailableError("offline"), ExternalServiceError),
        (
            ExternalServiceResponseError("bad response", status_code=500),
            ExternalServiceError,
        ),
        (InvalidExternalDataError("invalid"), ExternalServiceError),
        (InactiveApplicationError("inactive"), ExternalServiceError),
        (RateLimitExceededError("limited"), ExternalServiceError),
        (UnauthorizedError("unauthorized"), ExternalServiceError),
        (TokenError("token"), ApplicationError),
        (TokenStorageError("storage"), TokenError),
    ],
)
def test_application_error_hierarchy(error: Exception, base: type[Exception]) -> None:
    assert isinstance(error, base)
