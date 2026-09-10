import pytest

from src.infrastructure.strava.heart_rate_zone_mapper import map_heart_rate_zones
from tests.factories import zones_payload


def test_maps_heart_rate_zone_payload() -> None:
    result = map_heart_rate_zones(1, zones_payload())

    assert len(result.zones) == 5
    assert result.zones[0].time_seconds == 300
    assert result.zones[4].maximum_bpm is None


def test_selects_heart_rate_data_from_list_response() -> None:
    result = map_heart_rate_zones(
        1,
        [
            {"type": "power", "distribution_buckets": []},
            {"type": "heartrate", **zones_payload()},
        ],
    )

    assert len(result.zones) == 5


@pytest.mark.parametrize("payload", [[], [{"type": "power"}]])
def test_rejects_response_without_heart_rate_buckets(payload: object) -> None:
    with pytest.raises(ValueError, match="does not have heartrate"):
        map_heart_rate_zones(1, payload)


def test_rejects_non_object_bucket() -> None:
    with pytest.raises(TypeError, match="bucket must be an object"):
        map_heart_rate_zones(
            1,
            {"distribution_buckets": [1, 2, 3, 4, 5]},
        )


def test_rejects_non_integer_bucket_values() -> None:
    payload = zones_payload()
    buckets = payload["distribution_buckets"]
    assert isinstance(buckets, list)
    buckets[0] = {"min": "zero", "max": 120, "time": 1}

    with pytest.raises(TypeError, match="zone min must be an integer"):
        map_heart_rate_zones(1, payload)


@pytest.mark.parametrize(
    ("payload", "error_type", "message"),
    [
        ("invalid", TypeError, "object or a sequence"),
        ({"distribution_buckets": None}, ValueError, "heartrate information"),
        ({"distribution_buckets": []}, ValueError, "exactly five"),
        ({"distribution_buckets": "invalid"}, TypeError, "must be a sequence"),
    ],
)
def test_rejects_invalid_zone_responses(
    payload: object,
    error_type: type[Exception],
    message: str,
) -> None:
    with pytest.raises(error_type, match=message):
        map_heart_rate_zones(1, payload)
