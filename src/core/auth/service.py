import time
from collections.abc import Callable

from src.domain.token import TokenSet
from src.interfaces.auth import AuthorizationCodeProvider, TokenGateway, TokenStore
from src.utils.constants import OAUTH_URL


class AccessTokenService:
    """Return a valid token while hiding OAuth and persistence details."""

    def __init__(
        self,
        token_store: TokenStore,
        token_gateway: TokenGateway,
        authorization_code_provider: AuthorizationCodeProvider,
        client_id: str,
        clock: Callable[[], float] = time.time,
    ) -> None:
        self._token_store = token_store
        self._token_gateway = token_gateway
        self._authorization_code_provider = authorization_code_provider
        self._client_id = client_id
        self._clock = clock

    def get_access_token(self) -> str:
        tokens = self._token_store.load()
        if tokens is None:
            tokens = self._authorize()
        elif tokens.is_expired(int(self._clock())):
            tokens = self._refresh(tokens)

        return tokens.access_token

    def invalidate(self) -> None:
        self._token_store.clear()

    def _authorize(self) -> TokenSet:
        code = self._authorization_code_provider.get_authorization_code(
            OAUTH_URL,
            {
                "client_id": self._client_id,
                "response_type": "code",
                "redirect_uri": "http://localhost/exchange_token",
                "approval_prompt": "force",
                "scope": "read,read_all,activity:read,activity:read_all",
            },
        )
        return self._save(self._token_gateway.exchange_authorization_code(code))

    def _refresh(self, tokens: TokenSet) -> TokenSet:
        return self._save(
            self._token_gateway.refresh_access_token(tokens.refresh_token)
        )

    def _save(self, tokens: TokenSet) -> TokenSet:
        self._token_store.save(tokens)
        return tokens
