from collections.abc import Mapping
from typing import Protocol

from src.domain.token import TokenSet


class TokenStore(Protocol):
    """Persistence port for one current OAuth token set."""

    def load(self) -> TokenSet | None: ...

    def save(self, tokens: TokenSet) -> None: ...

    def clear(self) -> None: ...


class TokenGateway(Protocol):
    """Port for exchanging and refreshing OAuth tokens."""

    def exchange_authorization_code(self, code: str) -> TokenSet: ...

    def refresh_access_token(self, refresh_token: str) -> TokenSet: ...


class AuthorizationCodeProvider(Protocol):
    """Port that obtains an OAuth authorization code from the user."""

    def get_authorization_code(
        self, base_url: str, params: Mapping[str, str]
    ) -> str: ...
