import pytest

from src.domain.token import TokenSet
from src.infrastructure.serialization.token import token_from_mapping, token_to_mapping


def test_token_mapping_round_trip() -> None:
    tokens = TokenSet("access", "refresh", 123)

    assert token_from_mapping(token_to_mapping(tokens)) == tokens


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        ([], "must be an object"),
        ({"refresh_token": "refresh", "expires_at": 123}, "access_token"),
        ({"access_token": "access", "expires_at": 123}, "refresh_token"),
        (
            {"access_token": "access", "refresh_token": "refresh", "expires_at": "123"},
            "expires_at",
        ),
    ],
)
def test_rejects_invalid_token_payload(payload: object, message: str) -> None:
    with pytest.raises(TypeError, match=message):
        token_from_mapping(payload)
