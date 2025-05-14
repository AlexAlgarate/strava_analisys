import pytest

from src.utils.exceptions import (
    DatabaseOperationError,
    NotActivitiesError,
    TokenError,
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

    def test_database_operation_error(self) -> None:
        with pytest.raises(DatabaseOperationError):
            raise DatabaseOperationError("Database connection failed")

    def test_token_error(self) -> None:
        with pytest.raises(TokenError):
            raise TokenError("Invalid token")

    def test_unauthorized_error(self) -> None:
        with pytest.raises(UnauthorizedError):
            raise UnauthorizedError("Unauthorized access")
