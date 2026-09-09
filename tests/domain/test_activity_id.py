from typing import cast

import pytest

from src.domain.activity_id import require_activity_id


def test_returns_valid_activity_id() -> None:
    assert require_activity_id(42) == 42


@pytest.mark.parametrize("value", [True, 1.5, "1", None])
def test_rejects_non_integer_activity_id(value: object) -> None:
    with pytest.raises(TypeError, match="must be an integer"):
        require_activity_id(value)


@pytest.mark.parametrize("value", [0, -1])
def test_rejects_non_positive_activity_id(value: int) -> None:
    with pytest.raises(ValueError, match="must be a positive integer"):
        require_activity_id(cast(object, value))
