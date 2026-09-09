from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.access_token import GetAccessToken
from src.core.auth.service import AccessTokenService


def test_access_token_facade_delegates_to_service() -> None:
    service = Mock(spec=AccessTokenService)
    service.get_access_token.return_value = "access-token"

    provider = GetAccessToken(service=service)

    assert provider.get_access_token() == "access-token"
    service.get_access_token.assert_called_once_with()


@patch("src.access_token.load_dotenv")
def test_builds_local_service_without_external_database(
    load_dotenv: Mock, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("STRAVA_CLIENT_ID", "client-id")
    monkeypatch.setenv("STRAVA_SECRET_KEY", "secret")
    key_path = tmp_path / "key"
    token_path = tmp_path / "token"

    provider = GetAccessToken(token_path=token_path, key_path=key_path)

    assert isinstance(provider._service, AccessTokenService)
    assert key_path.exists()
    assert not token_path.exists()
    load_dotenv.assert_called_once_with()
