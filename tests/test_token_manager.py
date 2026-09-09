from unittest.mock import MagicMock, patch

import pytest
import requests

from src.domain.token import TokenSet
from src.infrastructure.auth.strava_token_gateway import GrantType, StravaTokenGateway
from src.utils.constants import URL_GET_ACCESS_TOKEN
from src.utils.exceptions import TokenError

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


def test_prepare_refresh_request(gateway: StravaTokenGateway) -> None:
    assert gateway._prepare_request_data(
        GrantType.REFRESH_TOKEN, refresh_token="refresh"
    ) == {
        "client_id": TEST_CLIENT_ID,
        "client_secret": TEST_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": "refresh",
    }


@patch("src.infrastructure.auth.strava_token_gateway.requests.post")
def test_exchange_authorization_code(
    post: MagicMock, gateway: StravaTokenGateway
) -> None:
    post.return_value.json.return_value = TEST_PAYLOAD

    result = gateway.exchange_authorization_code("oauth-code")

    assert result == TokenSet("access", "refresh", 2_000_000_000)
    post.assert_called_once_with(
        URL_GET_ACCESS_TOKEN,
        data={
            "client_id": TEST_CLIENT_ID,
            "client_secret": TEST_SECRET,
            "grant_type": "authorization_code",
            "code": "oauth-code",
        },
        timeout=3.0,
    )
    post.return_value.raise_for_status.assert_called_once_with()


@patch("src.infrastructure.auth.strava_token_gateway.requests.post")
def test_refresh_access_token(post: MagicMock, gateway: StravaTokenGateway) -> None:
    post.return_value.json.return_value = TEST_PAYLOAD

    result = gateway.refresh_access_token("old-refresh")

    assert result.access_token == "access"
    assert post.call_args.kwargs["data"]["refresh_token"] == "old-refresh"


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
    post.return_value.json.return_value = []

    with pytest.raises(TokenError, match="Could not obtain OAuth tokens"):
        gateway.exchange_authorization_code("code")
