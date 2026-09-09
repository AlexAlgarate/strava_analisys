from unittest.mock import Mock

import pytest

from src.infrastructure.auth.browser_authorization import (
    BrowserAuthorizationCodeProvider,
    StravaAuthorizationConfig,
)


def test_builds_strava_authorization_query() -> None:
    config = StravaAuthorizationConfig("client-id")

    assert config.as_query_params() == {
        "client_id": "client-id",
        "response_type": "code",
        "redirect_uri": "http://localhost/exchange_token",
        "approval_prompt": "force",
        "scope": "read,read_all,activity:read,activity:read_all",
    }


def test_rejects_empty_client_id() -> None:
    with pytest.raises(ValueError, match="cannot be empty"):
        StravaAuthorizationConfig("")


def test_reads_code_from_browser_redirect(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    browser_open = Mock()
    monkeypatch.setattr("webbrowser.open", browser_open)
    monkeypatch.setattr(
        "builtins.input",
        lambda: "http://localhost/exchange_token?state=x&code=secret-code",
    )
    provider = BrowserAuthorizationCodeProvider(
        StravaAuthorizationConfig("client-id")
    )

    assert provider.get_authorization_code() == "secret-code"
    opened_url = browser_open.call_args.args[0]
    assert opened_url.startswith("https://www.strava.com/oauth/authorize?")
    assert "client_id=client-id" in opened_url


@pytest.mark.parametrize(
    "url",
    [
        "http://localhost/exchange_token",
        "http://localhost/exchange_token?code=",
    ],
)
def test_rejects_redirect_without_code(url: str) -> None:
    with pytest.raises(ValueError, match="No authorization code"):
        BrowserAuthorizationCodeProvider._extract_code(url)
