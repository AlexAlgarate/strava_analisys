import pytest

from src.domain.token import TokenSet


def test_token_set_round_trip() -> None:
    tokens = TokenSet("access", "refresh", 123)

    assert TokenSet.from_mapping(tokens.as_dict()) == tokens


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        ({"refresh_token": "refresh", "expires_at": 123}, "access_token"),
        ({"access_token": "access", "expires_at": 123}, "refresh_token"),
        (
            {"access_token": "access", "refresh_token": "refresh", "expires_at": "123"},
            "expires_at",
        ),
    ],
)
def test_token_set_rejects_invalid_payload(
    payload: dict[str, object], message: str
) -> None:
    with pytest.raises(TypeError, match=message):
        TokenSet.from_mapping(payload)


@pytest.mark.parametrize(
    "tokens",
    [TokenSet("access", "refresh", 100), TokenSet("access", "refresh", 99)],
)
def test_token_set_is_expired_at_or_after_expiry(tokens: TokenSet) -> None:
    assert tokens.is_expired(now=100)


def test_token_set_is_not_expired_before_expiry() -> None:
    assert not TokenSet("access", "refresh", 101).is_expired(now=100)


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
