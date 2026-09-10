from unittest.mock import MagicMock, patch

import pytest
import requests

from src.application.errors import TokenError
from src.domain.token import TokenSet
from src.infrastructure.auth.strava_token_gateway import (
    TOKEN_URL,
    StravaTokenGateway,
)

TEST_CLIENT_ID = "test-client-id"
TEST_SECRET = "test-secret"
TEST_PAYLOAD: dict[str, object] = {
    "access_token": "access",
    "refresh_token": "refresh",
    "expires_at": 2_000_000_000,
}


@pytest.fixture
def gateway() -> StravaTokenGateway:
    return StravaTokenGateway(TEST_CLIENT_ID, TEST_SECRET, request_timeout=3.0)


@patch("src.infrastructure.auth.strava_token_gateway.requests.post")
def test_exchange_authorization_code(
    post: MagicMock, gateway: StravaTokenGateway
) -> None:
    post.return_value.status_code = 200
    post.return_value.json.return_value = TEST_PAYLOAD

    result = gateway.exchange_authorization_code("oauth-code")

    assert result == TokenSet("access", "refresh", 2_000_000_000)
    post.assert_called_once_with(
        TOKEN_URL,
        data={
            "client_id": TEST_CLIENT_ID,
            "client_secret": TEST_SECRET,
            "grant_type": "authorization_code",
            "code": "oauth-code",
        },
        timeout=3.0,
        allow_redirects=False,
    )
    post.return_value.raise_for_status.assert_called_once_with()


@patch("src.infrastructure.auth.strava_token_gateway.requests.post")
def test_refresh_access_token(post: MagicMock, gateway: StravaTokenGateway) -> None:
    post.return_value.status_code = 200
    post.return_value.json.return_value = TEST_PAYLOAD

    result = gateway.refresh_access_token("old-refresh")

    assert result == TokenSet("access", "refresh", 2_000_000_000)
    post.assert_called_once_with(
        TOKEN_URL,
        data={
            "client_id": TEST_CLIENT_ID,
            "client_secret": TEST_SECRET,
            "grant_type": "refresh_token",
            "refresh_token": "old-refresh",
        },
        timeout=3.0,
        allow_redirects=False,
    )
    post.return_value.raise_for_status.assert_called_once_with()


@patch("src.infrastructure.auth.strava_token_gateway.requests.post")
def test_request_failure_is_translated(
    post: MagicMock, gateway: StravaTokenGateway
) -> None:
    post.side_effect = requests.ConnectionError("offline")

    with pytest.raises(TokenError, match="Could not obtain OAuth tokens"):
        gateway.refresh_access_token("refresh")


@patch("src.infrastructure.auth.strava_token_gateway.requests.post")
def test_invalid_response_is_translated(
    post: MagicMock, gateway: StravaTokenGateway
) -> None:
    post.return_value.status_code = 200
    post.return_value.json.return_value = []

    with pytest.raises(TokenError, match="Could not obtain OAuth tokens"):
        gateway.exchange_authorization_code("code")


@pytest.mark.parametrize(
    ("client_id", "secret_key", "message"),
    [
        ("", TEST_SECRET, "client ID"),
        ("   ", TEST_SECRET, "client ID"),
        (TEST_CLIENT_ID, "", "client secret"),
        (TEST_CLIENT_ID, "\t", "client secret"),
    ],
)
def test_rejects_blank_credentials(
    client_id: str,
    secret_key: str,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        StravaTokenGateway(client_id, secret_key)


@pytest.mark.parametrize(
    "credentials",
    [
        (123, TEST_SECRET),
        (TEST_CLIENT_ID, None),
    ],
)
def test_rejects_non_string_credentials(credentials: tuple[object, object]) -> None:
    client_id, secret_key = credentials
    with pytest.raises(TypeError, match="must be a string"):
        StravaTokenGateway(
            client_id,  # ty: ignore[invalid-argument-type]
            secret_key,  # ty: ignore[invalid-argument-type]
        )


@pytest.mark.parametrize(
    "timeout",
    [
        pytest.param(0.0, id="zero"),
        pytest.param(-1.0, id="negative"),
        pytest.param(float("inf"), id="positive-infinity"),
        pytest.param(float("-inf"), id="negative-infinity"),
        pytest.param(float("nan"), id="nan"),
        pytest.param(10**10_000, id="unrepresentable"),
    ],
)
def test_rejects_invalid_request_timeout(timeout: int | float) -> None:
    with pytest.raises(ValueError, match="timeout"):
        StravaTokenGateway(TEST_CLIENT_ID, TEST_SECRET, request_timeout=timeout)


def test_rejects_boolean_request_timeout() -> None:
    with pytest.raises(TypeError, match="timeout"):
        StravaTokenGateway(
            TEST_CLIENT_ID,
            TEST_SECRET,
            request_timeout=True,
        )


@pytest.mark.parametrize("code", ["", " ", "\t"])
def test_rejects_blank_authorization_code(
    code: str,
    gateway: StravaTokenGateway,
) -> None:
    with pytest.raises(ValueError, match="Authorization code"):
        gateway.exchange_authorization_code(code)


@pytest.mark.parametrize("refresh_token", ["", " ", "\t"])
def test_rejects_blank_refresh_token(
    refresh_token: str,
    gateway: StravaTokenGateway,
) -> None:
    with pytest.raises(ValueError, match="Refresh token"):
        gateway.refresh_access_token(refresh_token)


def test_rejects_non_string_grant_inputs(gateway: StravaTokenGateway) -> None:
    with pytest.raises(TypeError, match="Authorization code"):
        gateway.exchange_authorization_code(
            None  # ty: ignore[invalid-argument-type]
        )
    with pytest.raises(TypeError, match="Refresh token"):
        gateway.refresh_access_token(123)  # ty: ignore[invalid-argument-type]


@patch("src.infrastructure.auth.strava_token_gateway.requests.post")
def test_rejects_redirect_response(
    post: MagicMock,
    gateway: StravaTokenGateway,
) -> None:
    post.return_value.status_code = 307

    with pytest.raises(TokenError, match="Could not obtain OAuth tokens"):
        gateway.refresh_access_token("refresh")

    post.assert_called_once_with(
        TOKEN_URL,
        data={
            "client_id": TEST_CLIENT_ID,
            "client_secret": TEST_SECRET,
            "grant_type": "refresh_token",
            "refresh_token": "refresh",
        },
        timeout=3.0,
        allow_redirects=False,
    )
    post.return_value.json.assert_not_called()
