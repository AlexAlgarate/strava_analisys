from unittest.mock import Mock

import pytest

from src.application.ports.authentication import (
    AuthorizationCodeProvider,
    TokenGateway,
    TokenStore,
)
from src.application.use_cases.authentication import AccessTokenService
from src.domain.token import TokenSet


@pytest.fixture
def token_store() -> Mock:
    return Mock(spec=TokenStore)


@pytest.fixture
def token_gateway() -> Mock:
    return Mock(spec=TokenGateway)


@pytest.fixture
def code_provider() -> Mock:
    return Mock(spec=AuthorizationCodeProvider)


def make_service(
    token_store: Mock,
    token_gateway: Mock,
    code_provider: Mock,
    *,
    now: float = 100.0,
) -> AccessTokenService:
    return AccessTokenService(
        token_store=token_store,
        token_gateway=token_gateway,
        authorization_code_provider=code_provider,
        clock=lambda: now,
    )


def test_returns_stored_token_when_valid(
    token_store: Mock,
    token_gateway: Mock,
    code_provider: Mock,
) -> None:
    token_store.load.return_value = TokenSet("stored", "refresh", 101)

    result = make_service(token_store, token_gateway, code_provider).get_access_token()

    assert result == "stored"
    token_gateway.refresh_access_token.assert_not_called()
    code_provider.get_authorization_code.assert_not_called()


def test_refreshes_and_persists_expired_token(
    token_store: Mock,
    token_gateway: Mock,
    code_provider: Mock,
) -> None:
    token_store.load.return_value = TokenSet("old", "old-refresh", 100)
    refreshed = TokenSet("new", "new-refresh", 200)
    token_gateway.refresh_access_token.return_value = refreshed

    result = make_service(token_store, token_gateway, code_provider).get_access_token()

    assert result == "new"
    token_gateway.refresh_access_token.assert_called_once_with("old-refresh")
    token_store.save.assert_called_once_with(refreshed)


def test_authorizes_and_persists_when_token_is_missing(
    token_store: Mock,
    token_gateway: Mock,
    code_provider: Mock,
) -> None:
    token_store.load.return_value = None
    code_provider.get_authorization_code.return_value = "oauth-code"
    issued = TokenSet("new", "refresh", 200)
    token_gateway.exchange_authorization_code.return_value = issued

    result = make_service(token_store, token_gateway, code_provider).get_access_token()

    assert result == "new"
    code_provider.get_authorization_code.assert_called_once_with()
    token_gateway.exchange_authorization_code.assert_called_once_with("oauth-code")
    token_store.save.assert_called_once_with(issued)


def test_invalidate_clears_store(
    token_store: Mock,
    token_gateway: Mock,
    code_provider: Mock,
) -> None:
    make_service(token_store, token_gateway, code_provider).invalidate()

    token_store.clear.assert_called_once_with()
