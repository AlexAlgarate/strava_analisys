import time
from collections.abc import Callable

from src.application.ports.authentication import (
    AuthorizationCodeProvider,
    TokenGateway,
    TokenStore,
)
from src.domain.token import TokenSet

DEFAULT_EXPIRY_LEEWAY_SECONDS = 60


class AccessTokenService:
    """Return a valid token while hiding OAuth and persistence details."""

    def __init__(
        self,
        token_store: TokenStore,
        token_gateway: TokenGateway,
        authorization_code_provider: AuthorizationCodeProvider,
        clock: Callable[[], float] = time.time,
        expiry_leeway_seconds: int = DEFAULT_EXPIRY_LEEWAY_SECONDS,
    ) -> None:
        if isinstance(expiry_leeway_seconds, bool) or not isinstance(
            expiry_leeway_seconds, int
        ):
            raise TypeError("Token expiry leeway must be an integer.")
        if expiry_leeway_seconds < 0:
            raise ValueError("Token expiry leeway cannot be negative.")
        self._token_store = token_store
        self._token_gateway = token_gateway
        self._authorization_code_provider = authorization_code_provider
        self._clock = clock
        self._expiry_leeway_seconds = expiry_leeway_seconds

    def get_access_token(self) -> str:
        tokens = self._token_store.load()
        if tokens is None:
            tokens = self._authorize()
        elif tokens.is_expired(int(self._clock()) + self._expiry_leeway_seconds):
            tokens = self._refresh(tokens)
        return tokens.access_token

    def invalidate(self) -> None:
        self._token_store.clear()

    def _authorize(self) -> TokenSet:
        code = self._authorization_code_provider.get_authorization_code()
        return self._save(self._token_gateway.exchange_authorization_code(code))

    def _refresh(self, tokens: TokenSet) -> TokenSet:
        return self._save(
            self._token_gateway.refresh_access_token(tokens.refresh_token)
        )

    def _save(self, tokens: TokenSet) -> TokenSet:
        self._token_store.save(tokens)
        return tokens
