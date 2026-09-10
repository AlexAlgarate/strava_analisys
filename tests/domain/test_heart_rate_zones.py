from collections.abc import Callable
from dataclasses import replace
from typing import cast

import pytest

from src.domain.heart_rate_zones import HeartRateZone, HeartRateZones
from tests.factories import heart_rate_zones


def _unchecked_heart_rate_zones(**kwargs: object) -> HeartRateZones:
    """Exercise runtime validation with values outside the static contract."""
    factory = cast(Callable[..., HeartRateZones], HeartRateZones)
    return factory(**kwargs)


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


def test_requires_contiguous_zones_with_only_the_last_unbounded() -> None:
    zones = heart_rate_zones().zones

    with pytest.raises(ValueError, match="Only the final"):
        HeartRateZones(
            activity_id=1,
            zones=(replace(zones[0], maximum_bpm=None), *zones[1:]),
        )
    with pytest.raises(ValueError, match="final heart-rate zone"):
        HeartRateZones(
            activity_id=1,
            zones=(*zones[:-1], replace(zones[-1], maximum_bpm=200)),
        )
    with pytest.raises(ValueError, match="contiguous"):
        HeartRateZones(
            activity_id=1,
            zones=(zones[0], replace(zones[1], minimum_bpm=121), *zones[2:]),
        )


def test_requires_typed_zone_tuple() -> None:
    with pytest.raises(TypeError, match="tuple of HeartRateZone"):
        _unchecked_heart_rate_zones(
            activity_id=1,
            zones=[*heart_rate_zones().zones],
        )


@pytest.mark.parametrize(
    ("values", "message"),
    [
        ((0, 0, 100, 1), "between one and five"),
        ((1, -1, 100, 1), "minimum cannot be negative"),
        ((1, 120, 120, 1), "maximum must exceed"),
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
    with pytest.raises(TypeError, match="maximum must be an integer"):
        HeartRateZone(1, 0, cast(int, True), 1)
