import pytest

from src.utils.exceptions import (
    NotActivitiesError,
    TokenError,
    TokenStorageError,
    TooManyRequestError,
    UnauthorizedError,
)


class TestExceptions:
    def test_not_activities_error(self) -> None:
        with pytest.raises(NotActivitiesError):
            raise NotActivitiesError("No activities found")

    def test_too_many_request_error(self) -> None:
        with pytest.raises(TooManyRequestError):
            raise TooManyRequestError("Rate limit exceeded")

    def test_token_storage_error_is_a_token_error(self) -> None:
        with pytest.raises(TokenError):
            raise TokenStorageError("Token file could not be read")

    def test_token_error(self) -> None:
        with pytest.raises(TokenError):
            raise TokenError("Invalid token")

    def test_unauthorized_error(self) -> None:
        with pytest.raises(UnauthorizedError):
            raise UnauthorizedError("Unauthorized access")
