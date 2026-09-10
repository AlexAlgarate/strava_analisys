from typing import cast

import pytest

from src.domain.token import TokenSet


@pytest.mark.parametrize(
    "tokens",
    [TokenSet("access", "refresh", 100), TokenSet("access", "refresh", 99)],
)
def test_token_set_is_expired_at_or_after_expiry(tokens: TokenSet) -> None:
    assert tokens.is_expired(now=100)


def test_token_set_is_not_expired_before_expiry() -> None:
    assert not TokenSet("access", "refresh", 101).is_expired(now=100)


def test_token_set_repr_does_not_expose_credentials() -> None:
    representation = repr(TokenSet("secret-access", "secret-refresh", 100))

    assert "secret-access" not in representation
    assert "secret-refresh" not in representation
    assert "expires_at=100" in representation


@pytest.mark.parametrize(
    ("access_token", "refresh_token", "expires_at", "message"),
    [
        ("", "refresh", 100, "Access token"),
        ("access", "", 100, "Refresh token"),
        ("access", "refresh", 0, "expiration"),
    ],
)
def test_token_set_rejects_invalid_values(
    access_token: str,
    refresh_token: str,
    expires_at: int,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        TokenSet(access_token, refresh_token, expires_at)


@pytest.mark.parametrize(
    ("values", "message"),
    [
        ((1, "refresh", 100), "Access token"),
        (("access", 1, 100), "Refresh token"),
        (("access", "refresh", True), "expiration"),
    ],
)
def test_token_set_rejects_invalid_types(
    values: tuple[object, object, object],
    message: str,
) -> None:
    with pytest.raises(TypeError, match=message):
        TokenSet(
            cast(str, values[0]),
            cast(str, values[1]),
            cast(int, values[2]),
        )
