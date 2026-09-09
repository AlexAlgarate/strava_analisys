from collections.abc import MutableMapping
from dataclasses import FrozenInstanceError
from datetime import datetime
from typing import cast

import pytest

from src.domain.detailed_activity import DetailedActivity
from tests.factories import activity_payload


def test_builds_activity_from_api_mapping() -> None:
    activity = DetailedActivity.from_mapping(
        activity_payload(gear={"id": "g1", "primary": True})
    )

    assert activity.id == 1
    assert activity.start_date_local == datetime.fromisoformat("2026-09-07T07:30:00")
    assert activity.distance == 10_000
    assert activity.gear == {"id": "g1", "primary": True}


def test_optional_metrics_are_represented_as_missing() -> None:
    payload = activity_payload()
    for key in (
        "average_heartrate",
        "max_heartrate",
        "calories",
        "perceived_exertion",
        "average_speed",
    ):
        payload.pop(key)

    activity = DetailedActivity.from_mapping(payload)

    assert activity.average_heartrate is None
    assert activity.total_elevation_gain == 120
    assert "average_heartrate" not in activity.as_dict()


@pytest.mark.parametrize(
    ("field", "value", "error_type"),
    [
        ("id", True, TypeError),
        ("name", 42, TypeError),
        ("distance", "far", TypeError),
        ("moving_time", 1.5, TypeError),
        ("start_date_local", "not-a-date", ValueError),
        ("gear", [], TypeError),
    ],
)
def test_rejects_invalid_api_fields(
    field: str,
    value: object,
    error_type: type[Exception],
) -> None:
    payload = activity_payload()
    payload[field] = value

    with pytest.raises(error_type):
        DetailedActivity.from_mapping(payload)


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"distance": -1}, "distance"),
        ({"moving_time": -1}, "moving_time"),
        ({"elapsed_time": 3_000}, "shorter"),
        ({"perceived_exertion": 11}, "between 0 and 10"),
        (
            {"average_heartrate": 180, "max_heartrate": 170},
            "cannot exceed",
        ),
    ],
)
def test_enforces_domain_invariants(changes: dict[str, object], message: str) -> None:
    payload = activity_payload()
    payload.update(changes)

    with pytest.raises(ValueError, match=message):
        DetailedActivity.from_mapping(payload)


def test_activity_and_nested_gear_are_immutable() -> None:
    activity = DetailedActivity.from_mapping(activity_payload(gear={"id": "g1"}))

    attribute_name = "name"
    with pytest.raises(FrozenInstanceError):
        setattr(activity, attribute_name, "Changed")
    assert activity.gear is not None
    mutable_gear = cast(MutableMapping[str, object], activity.gear)
    with pytest.raises(TypeError):
        mutable_gear["id"] = "g2"
