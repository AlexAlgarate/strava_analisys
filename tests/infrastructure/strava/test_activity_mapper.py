from datetime import datetime

import pytest

from src.infrastructure.strava.activity_mapper import map_activity, map_activity_list
from tests.factories import activity_payload


def test_maps_activity_payload() -> None:
    activity = map_activity(activity_payload(gear_id="g1"))

    assert activity.id == 1
    assert activity.start_date_local == datetime.fromisoformat(
        "2026-09-07T07:30:00+02:00"
    )
    assert activity.gear_id == "g1"


def test_maps_activity_list() -> None:
    activities = map_activity_list([activity_payload(1), activity_payload(2)])

    assert [activity.id for activity in activities] == [1, 2]


def test_optional_metrics_default_to_missing() -> None:
    payload = activity_payload()
    for key in (
        "average_heartrate",
        "max_heartrate",
        "calories",
        "perceived_exertion",
        "average_speed",
    ):
        payload.pop(key)

    activity = map_activity(payload)

    assert activity.average_heartrate is None
    assert activity.total_elevation_gain == 120


@pytest.mark.parametrize(
    ("field", "value", "error_type"),
    [
        ("id", True, TypeError),
        ("name", 42, TypeError),
        ("distance", "far", TypeError),
        ("moving_time", 1.5, TypeError),
        ("start_date_local", "not-a-date", ValueError),
        ("start_date_local", "2026-09-07T07:30:00", ValueError),
        ("gear_id", 42, TypeError),
    ],
)
def test_rejects_invalid_activity_fields(
    field: str,
    value: object,
    error_type: type[Exception],
) -> None:
    payload = activity_payload()
    payload[field] = value

    with pytest.raises(error_type):
        map_activity(payload)


@pytest.mark.parametrize("payload", [{"id": 1}, "invalid"])
def test_rejects_invalid_activity_collections(payload: object) -> None:
    with pytest.raises(TypeError, match="response must be a list"):
        map_activity_list(payload)


def test_rejects_non_object_activity() -> None:
    with pytest.raises(TypeError, match="must be an object"):
        map_activity("invalid")


@pytest.mark.parametrize("field", ["distance", "average_speed"])
def test_rejects_numbers_too_large_for_float(field: str) -> None:
    payload = activity_payload()
    payload[field] = 10**400

    with pytest.raises(ValueError, match=rf"Activity {field} must be finite") as error:
        map_activity(payload)

    assert isinstance(error.value.__cause__, OverflowError)


def test_rejects_a_duration_too_large_for_domain_calculations() -> None:
    with pytest.raises(ValueError, match="supported duration range") as error:
        map_activity(activity_payload(moving_time=10**100, elapsed_time=10**100))

    assert isinstance(error.value.__cause__, OverflowError)
