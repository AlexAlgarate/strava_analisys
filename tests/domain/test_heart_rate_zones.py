from dataclasses import replace
from typing import cast

import pytest

from src.domain.heart_rate_zones import HeartRateZone, HeartRateZones
from tests.factories import heart_rate_zones


@pytest.mark.parametrize("activity_id", [True, 0])
def test_rejects_invalid_activity_id(activity_id: object) -> None:
    expected_error = TypeError if activity_id is True else ValueError

    with pytest.raises(expected_error):
        replace(heart_rate_zones(), activity_id=cast(int, activity_id))


def test_requires_exactly_five_zones() -> None:
    with pytest.raises(ValueError, match="exactly five"):
        HeartRateZones(activity_id=1, zones=())


def test_requires_zones_ordered_from_one_to_five() -> None:
    zones = heart_rate_zones().zones

    with pytest.raises(ValueError, match="ordered"):
        HeartRateZones(activity_id=1, zones=(zones[1], zones[0], *zones[2:]))


@pytest.mark.parametrize(
    ("values", "message"),
    [
        ((0, 0, 100, 1), "between one and five"),
        ((1, -1, 100, 1), "minimum cannot be negative"),
        ((1, 120, 100, 1), "maximum must exceed"),
        ((1, 0, 100, -1), "time cannot be negative"),
    ],
)
def test_zone_enforces_business_invariants(
    values: tuple[int, int, int, int],
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        HeartRateZone(*values)


def test_zone_rejects_non_integer_values() -> None:
    with pytest.raises(TypeError, match="number must be an integer"):
        HeartRateZone(cast(int, True), 0, 100, 1)
