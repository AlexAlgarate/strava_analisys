from collections.abc import Mapping

from src.domain.token import TokenSet


def token_from_mapping(payload: object) -> TokenSet:
    """Decode an untrusted OAuth token mapping into a domain value."""
    if not isinstance(payload, Mapping):
        raise TypeError("Token payload must be an object.")

    access_token = payload.get("access_token")
    refresh_token = payload.get("refresh_token")
    expires_at = payload.get("expires_at")
    if not isinstance(access_token, str):
        raise TypeError("Token payload must contain a string access_token.")
    if not isinstance(refresh_token, str):
        raise TypeError("Token payload must contain a string refresh_token.")
    if isinstance(expires_at, bool) or not isinstance(expires_at, int):
        raise TypeError("Token payload must contain an integer expires_at.")
    return TokenSet(access_token, refresh_token, expires_at)


def token_to_mapping(tokens: TokenSet) -> dict[str, str | int]:
    """Encode a domain token value for an infrastructure boundary."""
    return {
        "access_token": tokens.access_token,
        "refresh_token": tokens.refresh_token,
        "expires_at": tokens.expires_at,
    }
