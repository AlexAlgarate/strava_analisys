from collections.abc import Callable, Iterator
from typing import cast
from urllib import parse

import pytest

from src.infrastructure.auth.browser_authorization import (
    BrowserAuthorizationCodeProvider,
    StravaAuthorizationConfig,
)


def test_builds_strava_authorization_query() -> None:
    config = StravaAuthorizationConfig("client-id")

    assert config.as_query_params(state="oauth-state") == {
        "client_id": "client-id",
        "response_type": "code",
        "redirect_uri": "http://localhost/exchange_token",
        "approval_prompt": "force",
        "scope": "read,activity:read_all",
        "state": "oauth-state",
    }


@pytest.mark.parametrize("client_id", ["", " ", "\t"])
def test_rejects_blank_client_id(client_id: str) -> None:
    with pytest.raises(ValueError, match="cannot be empty"):
        StravaAuthorizationConfig(client_id)


def test_rejects_non_string_client_id() -> None:
    config_factory = cast(
        Callable[..., StravaAuthorizationConfig],
        StravaAuthorizationConfig,
    )

    with pytest.raises(TypeError, match="must be a string"):
        config_factory(123)


def test_rejects_empty_oauth_state() -> None:
    with pytest.raises(ValueError, match="state cannot be empty"):
        StravaAuthorizationConfig("client-id").as_query_params(state="")


def test_rejects_invalid_oauth_state_type() -> None:
    query_factory = cast(
        Callable[..., dict[str, str]],
        StravaAuthorizationConfig("client-id").as_query_params,
    )

    with pytest.raises(TypeError, match="state must be a string"):
        query_factory(state=123)


def test_reads_code_from_matching_browser_redirect() -> None:
    opened_urls: list[str] = []
    provider = BrowserAuthorizationCodeProvider(
        StravaAuthorizationConfig("client-id"),
        opener=lambda url: opened_urls.append(url),
        input_reader=lambda _prompt: (
            "http://localhost/exchange_token?state=oauth-state&code=secret-code"
        ),
        state_factory=lambda: "oauth-state",
    )

    assert provider.get_authorization_code() == "secret-code"
    [opened_url] = opened_urls
    assert opened_url.startswith("https://www.strava.com/oauth/authorize?")
    assert parse.parse_qs(parse.urlsplit(opened_url).query) == {
        "approval_prompt": ["force"],
        "client_id": ["client-id"],
        "redirect_uri": ["http://localhost/exchange_token"],
        "response_type": ["code"],
        "scope": ["read,activity:read_all"],
        "state": ["oauth-state"],
    }


def test_requests_a_fresh_state_from_factory_for_each_attempt() -> None:
    states = iter(("first-state", "second-state"))
    callback_urls: Iterator[str] = iter(
        (
            "http://localhost/exchange_token?code=first&state=first-state",
            "http://localhost/exchange_token?code=second&state=second-state",
        )
    )
    opened_urls: list[str] = []
    provider = BrowserAuthorizationCodeProvider(
        StravaAuthorizationConfig("client-id"),
        opener=lambda url: opened_urls.append(url),
        input_reader=lambda _prompt: next(callback_urls),
        state_factory=lambda: next(states),
    )

    assert provider.get_authorization_code() == "first"
    assert provider.get_authorization_code() == "second"
    assert [
        parse.parse_qs(parse.urlsplit(url).query)["state"][0] for url in opened_urls
    ] == ["first-state", "second-state"]


def test_default_state_is_fresh_and_url_safe() -> None:
    opened_urls: list[str] = []

    def callback_for_last_request(_prompt: str) -> str:
        state = parse.parse_qs(parse.urlsplit(opened_urls[-1]).query)["state"][0]
        query = parse.urlencode({"code": "secret-code", "state": state})
        return f"http://localhost/exchange_token?{query}"

    provider = BrowserAuthorizationCodeProvider(
        StravaAuthorizationConfig("client-id"),
        opener=lambda url: opened_urls.append(url),
        input_reader=callback_for_last_request,
    )

    assert provider.get_authorization_code() == "secret-code"
    assert provider.get_authorization_code() == "secret-code"
    states = [
        parse.parse_qs(parse.urlsplit(url).query)["state"][0] for url in opened_urls
    ]
    assert states[0] != states[1]
    assert all(
        len(state) >= 32 and state.replace("_", "").replace("-", "").isalnum()
        for state in states
    )


@pytest.mark.parametrize(
    "url",
    [
        "http://localhost/exchange_token?state=expected",
        "http://localhost/exchange_token?state=expected&code=",
    ],
)
def test_rejects_redirect_without_code(url: str) -> None:
    with pytest.raises(ValueError, match="No authorization code"):
        BrowserAuthorizationCodeProvider._extract_code(
            url,
            expected_state="expected",
            redirect_uri="http://localhost/exchange_token",
        )


@pytest.mark.parametrize(
    "url",
    [
        "http://localhost/exchange_token?code=value",
        "http://localhost/exchange_token?code=value&state=",
    ],
)
def test_rejects_redirect_without_state(url: str) -> None:
    with pytest.raises(ValueError, match="No OAuth state"):
        BrowserAuthorizationCodeProvider._extract_code(
            url,
            expected_state="expected",
            redirect_uri="http://localhost/exchange_token",
        )


def test_rejects_mismatched_state() -> None:
    with pytest.raises(ValueError, match="does not match"):
        BrowserAuthorizationCodeProvider._extract_code(
            "http://localhost/exchange_token?code=value&state=attacker",
            expected_state="expected",
            redirect_uri="http://localhost/exchange_token",
        )


@pytest.mark.parametrize(
    "url",
    [
        "https://localhost/exchange_token?code=value&state=expected",
        "http://localhost.evil/exchange_token?code=value&state=expected",
        "http://localhost:80/exchange_token?code=value&state=expected",
        "http://localhost/other?code=value&state=expected",
        "http://localhost/exchange_token?code=value&state=expected#fragment",
    ],
)
def test_rejects_callback_from_unexpected_redirect(url: str) -> None:
    with pytest.raises(ValueError, match="does not match"):
        BrowserAuthorizationCodeProvider._extract_code(
            url,
            expected_state="expected",
            redirect_uri="http://localhost/exchange_token",
        )


@pytest.mark.parametrize(
    "query",
    [
        "code=one&code=two&state=expected",
        "code=value&state=one&state=two",
        "code=value&state=expected&scope=read&scope=read_all",
    ],
)
def test_rejects_duplicate_callback_parameters(query: str) -> None:
    with pytest.raises(ValueError, match="duplicated"):
        BrowserAuthorizationCodeProvider._extract_code(
            f"http://localhost/exchange_token?{query}",
            expected_state="expected",
            redirect_uri="http://localhost/exchange_token",
        )


def test_rejects_oauth_error_response() -> None:
    with pytest.raises(ValueError, match="authorization failed: access_denied"):
        BrowserAuthorizationCodeProvider._extract_code(
            "http://localhost/exchange_token?error=access_denied&state=expected",
            expected_state="expected",
            redirect_uri="http://localhost/exchange_token",
        )


def test_rejects_malformed_callback_query() -> None:
    with pytest.raises(ValueError, match="query is invalid"):
        BrowserAuthorizationCodeProvider._extract_code(
            "http://localhost/exchange_token?code=value&state=expected&broken",
            expected_state="expected",
            redirect_uri="http://localhost/exchange_token",
        )


@pytest.mark.parametrize(
    "redirect_uri",
    [
        "localhost/exchange_token",
        "http://localhost/exchange_token?existing=value",
        "http://localhost/exchange_token#fragment",
    ],
)
def test_rejects_invalid_configured_redirect_uri(redirect_uri: str) -> None:
    with pytest.raises(ValueError, match="redirect URI"):
        StravaAuthorizationConfig("client-id", redirect_uri=redirect_uri)


@pytest.mark.parametrize(
    "configuration",
    [
        {"authorization_url": "http://www.strava.com/oauth/authorize"},
        {"authorization_url": "https://user:secret@example.test/oauth"},
        {"redirect_uri": "http://example.test/exchange_token"},
        {"redirect_uri": "file:///tmp/exchange_token"},
        {"scope": " "},
    ],
)
def test_rejects_unsafe_authorization_configuration(
    configuration: dict[str, str],
) -> None:
    with pytest.raises(ValueError):
        StravaAuthorizationConfig("client-id", **configuration)
