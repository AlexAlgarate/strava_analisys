import time
from unittest.mock import patch

import pytest

from src.token_manager import Credentials, GranType, TokenException, TokenManager

TEST_CLIENT_ID = "test_client_id"
TEST_SECRET_KEY = "test_secret_key"
TEST_REFRESH_TOKEN = "test_refresh_token"
TEST_AUTHORIZATION_CODE = "test_auth_code"
TEST_ACCESS_TOKEN = "test_access_token"
TEST_BASE_URL_ACCESS_TOKEN = "https://www.strava.com/oauth/token"


@pytest.fixture
def token_manager():
    return TokenManager(
        client_id=TEST_CLIENT_ID,
        secret_key=TEST_SECRET_KEY,
    )


@pytest.fixture
def mock_successful_response():
    return {
        "access_token": TEST_ACCESS_TOKEN,
        "refresh_token": TEST_REFRESH_TOKEN,
        "expires_at": int(time.time()) + 3600,
    }


class TestTokenManager:
    def test_init_creates_credentials(self):
        manager = TokenManager(TEST_CLIENT_ID, TEST_SECRET_KEY)
        assert isinstance(manager.credentials, Credentials)
        assert manager.credentials.client_id == TEST_CLIENT_ID
        assert manager.credentials.secret_key == TEST_SECRET_KEY

    def test_init_sets_up_logger(self):
        TokenManager(TEST_CLIENT_ID, TEST_SECRET_KEY)

    def test_token_has_expired_with_expired_token(self):
        token_has_expired = int(time.time()) - 3600
        assert TokenManager.token_has_expired(expires_at=token_has_expired) is True

    def test_token_has_expired_with_valid_token(self):
        token_has_not_expired = int(time.time()) + 3600
        assert TokenManager.token_has_expired(expires_at=token_has_not_expired) is False

    def test_prepare_request_data_refresh_token(self, token_manager):
        data = token_manager._prepare_request_data(
            GranType.REFRESH_TOKEN, refresh_token=TEST_REFRESH_TOKEN
        )
        assert data == {
            "client_id": TEST_CLIENT_ID,
            "client_secret": TEST_SECRET_KEY,
            "grant_type": "refresh_token",
            "refresh_token": TEST_REFRESH_TOKEN,
        }

    def test_prepare_request_data_authorization_code(self, token_manager):
        data = token_manager._prepare_request_data(
            GranType.AUTHORIZATION_CODE, code=TEST_AUTHORIZATION_CODE
        )
        assert data == {
            "client_id": TEST_CLIENT_ID,
            "client_secret": TEST_SECRET_KEY,
            "grant_type": "authorization_code",
            "code": TEST_AUTHORIZATION_CODE,
        }

    @patch("requests.post")
    def test_send_token_request_success(
        self, mock_post, token_manager, mock_successful_response
    ):
        mock_post.return_value.json.return_value = mock_successful_response
        mock_post.return_value.raise_for_status.return_value = None

        result = token_manager._send_token_request({"test": "data"})

        assert result == mock_successful_response
        mock_post.assert_called_once_with(
            TEST_BASE_URL_ACCESS_TOKEN, data={"test": "data"}
        )
        mock_post.assert_called_once()

    @patch("requests.post")
    def test_send_token_request_failure(self, mock_post, token_manager):
        mock_post.side_effect = TokenException("API ERROR")

        result = token_manager._send_token_request({"test": "data"})

        assert result is None

    @patch("requests.post")
    def test_get_initial_tokens_success(
        self, mock_post, token_manager, mock_successful_response
    ):
        mock_post.return_value.json.return_value = mock_successful_response
        mock_post.return_value.raise_for_status.return_value = None

        result = token_manager.get_initial_tokens(TEST_AUTHORIZATION_CODE)

        assert result == mock_successful_response
        mock_post.assert_called_once_with(
            TEST_BASE_URL_ACCESS_TOKEN,
            data={
                "client_id": TEST_CLIENT_ID,
                "client_secret": TEST_SECRET_KEY,
                "grant_type": "authorization_code",
                "code": TEST_AUTHORIZATION_CODE,
            },
        )

    @patch("requests.post")
    def test_get_initial_tokens_failure(self, mock_post, token_manager):
        mock_post.side_effect = TokenException("API ERROR")

        result = token_manager.get_initial_tokens(TEST_AUTHORIZATION_CODE)

        assert result is None

    @patch("requests.post")
    def test_refresh_access_token_success(
        self, mock_post, token_manager, mock_successful_response
    ):
        mock_post.return_value.json.return_value = mock_successful_response
        mock_post.return_value.raise_for_status.return_value = None

        result = token_manager.refresh_access_token(TEST_REFRESH_TOKEN)

        assert result == mock_successful_response
        mock_post.assert_called_once_with(
            TEST_BASE_URL_ACCESS_TOKEN,
            data={
                "client_id": TEST_CLIENT_ID,
                "client_secret": TEST_SECRET_KEY,
                "grant_type": "refresh_token",
                "refresh_token": TEST_REFRESH_TOKEN,
            },
        )

    @patch("requests.post")
    def test_refresh_access_token_failure(self, mock_post, token_manager):
        mock_post.side_effect = TokenException("API ERROR")

        result = token_manager.refresh_access_token(TEST_REFRESH_TOKEN)

        assert result is None
