from typing import cast

import pytest

from src.domain.heart_rate_zones import HeartRateZone, HeartRateZones
from tests.factories import zones_payload


def test_uses_first_bucket_collection_when_type_is_absent() -> None:
    result = HeartRateZones.from_api_response(
        1,
        [{"unrelated": True}, zones_payload()],
    )

    assert result.zones[4].maximum_bpm == -1


@pytest.mark.parametrize("payload", [[], [{"type": "power"}]])
def test_rejects_a_response_without_heart_rate_buckets(payload: object) -> None:
    with pytest.raises(ValueError, match="does not have heartrate"):
        HeartRateZones.from_api_response(1, payload)


def test_rejects_non_object_bucket() -> None:
    with pytest.raises(TypeError, match="bucket must be an object"):
        HeartRateZones.from_api_response(
            1,
            {"distribution_buckets": [1, 2, 3, 4, 5]},
        )


def test_rejects_non_integer_bucket_values() -> None:
    payload = zones_payload()
    buckets = payload["distribution_buckets"]
    assert isinstance(buckets, list)
    buckets[0] = {"min": "zero", "max": 120, "time": 1}

    with pytest.raises(TypeError, match="zone min must be an integer"):
        HeartRateZones.from_api_response(1, payload)


@pytest.mark.parametrize("activity_id", [True, 0])
def test_rejects_invalid_activity_id(activity_id: object) -> None:
    zones = tuple(
        HeartRateZone(number=index, minimum_bpm=0, maximum_bpm=1, time_seconds=1)
        for index in range(1, 6)
    )
    expected_error = TypeError if activity_id is True else ValueError

    with pytest.raises(expected_error):
        HeartRateZones(activity_id=cast(int, activity_id), zones=zones)


def test_requires_exactly_five_zones() -> None:
    with pytest.raises(ValueError, match="exactly five"):
        HeartRateZones(activity_id=1, zones=())


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
