from unittest.mock import MagicMock, patch
from urllib.parse import parse_qs, urlparse

import pytest

from src.infrastructure.auth.oauth_code import GetOauthCode


class TestGetOauthCode:
    base_url = "https://example.com/auth"
    params = {
        "client_id": "123",
        "response_type": "code",
        "redirect_uri": "http://localhost/exchange_token",
        "approval_prompt": "force",
        "scope": "read,read_all,activity:read,activity:read_all",
    }

    @pytest.fixture
    def oauth_handler(self) -> GetOauthCode:
        return GetOauthCode()

    def test_create_full_url(self, oauth_handler: GetOauthCode) -> None:
        result = oauth_handler._create_full_url(self.base_url, self.params)

        parsed_url = urlparse(result)
        query_params = parse_qs(parsed_url.query)

        assert parsed_url.scheme == "https"
        assert parsed_url.netloc == "example.com"
        assert parsed_url.path == "/auth"
        assert query_params["client_id"][0] == "123"
        assert query_params["response_type"][0] == "code"
        assert query_params["redirect_uri"][0] == "http://localhost/exchange_token"
        assert query_params["approval_prompt"][0] == "force"
        assert (
            query_params["scope"][0] == "read,read_all,activity:read,activity:read_all"
        )

    def test_create_full_url_with_empty_params(
        self, oauth_handler: GetOauthCode
    ) -> None:
        params: dict = {}

        result = oauth_handler._create_full_url(self.base_url, params)
        assert result == self.base_url

    def test_extract_code_successful(self, oauth_handler: GetOauthCode) -> None:
        test_url = "https://example.com/callback?state=xyz&code=abc123def456&scope=read"
        code = oauth_handler._extract_code(test_url)
        assert code == "abc123def456"

    def test_extract_code_no_code(self, oauth_handler: GetOauthCode) -> None:
        test_url = "https://example.com/callback?state=xyz&scope=read"
        with pytest.raises(ValueError, match="No authorization code found in the URL"):
            oauth_handler._extract_code(test_url)

    @patch("webbrowser.open")
    @patch("builtins.input")
    def test_get_authorization_code(
        self,
        mock_input: MagicMock,
        mock_browser_open: MagicMock,
        oauth_handler: GetOauthCode,
    ) -> None:
        mock_input.return_value = (
            "https://example.com/callback?state=xyz&code=abc123def456&scope=read"
        )

        params = {
            "client_id": "123",
            "scope": "read write",
            "response_type": "code",
        }

        code = oauth_handler.get_authorization_code(self.base_url, params)

        mock_browser_open.assert_called_once()

        assert code == "abc123def456"

    @patch("webbrowser.open")
    @patch("builtins.input")
    def test_get_authorization_code_invalid_url(
        self,
        mock_input: MagicMock,
        mock_browser_open: MagicMock,
        oauth_handler: GetOauthCode,
    ) -> None:
        mock_input.return_value = "https://example.com/callback?state=xyz&scope=read"

        with pytest.raises(ValueError, match="No authorization code found in the URL"):
            oauth_handler.get_authorization_code(self.base_url, self.params)

    def test_create_full_url_with_special_characters(
        self, oauth_handler: GetOauthCode
    ) -> None:
        params = {
            "client_id": "123+456",
            "scope": "read write",
            "redirect_uri": "https://app.example.com/callback",
        }

        result = oauth_handler._create_full_url(self.base_url, params)
        parsed_url = urlparse(result)
        query_params = parse_qs(parsed_url.query)

        assert query_params["client_id"][0] == "123+456"
        assert query_params["redirect_uri"][0] == "https://app.example.com/callback"
