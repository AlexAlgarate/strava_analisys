from dataclasses import FrozenInstanceError, replace
from datetime import datetime
from typing import cast

import pytest

from tests.factories import activity_model


def _unknown(value: object) -> object:
    return value


def test_keeps_valid_activity_values() -> None:
    activity = activity_model(gear_id="g1")

    assert activity.id == 1
    assert activity.start_date_local == datetime.fromisoformat(
        "2026-09-07T07:30:00+02:00"
    )
    assert activity.distance == 10_000
    assert activity.gear_id == "g1"


@pytest.mark.parametrize(
    ("changes", "error_type"),
    [
        ({"id": True}, TypeError),
        ({"name": cast(str, _unknown(42))}, TypeError),
        ({"sport_type": cast(str, _unknown(42))}, TypeError),
        ({"distance": cast(float, _unknown("far"))}, TypeError),
        ({"moving_time": cast(int, _unknown(1.5))}, TypeError),
        ({"start_date_local": cast(datetime, _unknown("not-a-date"))}, TypeError),
        ({"gear_id": cast(str, _unknown(42))}, TypeError),
        ({"perceived_exertion": cast(int, _unknown(1.5))}, TypeError),
    ],
    ids=[
        "boolean-id",
        "non-string-name",
        "non-string-sport",
        "non-numeric-distance",
        "non-integer-moving-time",
        "non-datetime-start-date",
        "non-string-gear-id",
        "non-integer-exertion",
    ],
)
def test_rejects_invalid_field_types(
    changes: dict[str, object],
    error_type: type[Exception],
) -> None:
    with pytest.raises(error_type):
        replace(activity_model(), **changes)


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"name": ""}, "name cannot be empty"),
        ({"name": "   "}, "name cannot be empty"),
        ({"sport_type": ""}, "sport type cannot be empty"),
        ({"sport_type": "\t"}, "sport type cannot be empty"),
        ({"gear_id": ""}, "gear id cannot be empty"),
        ({"gear_id": "   "}, "gear id cannot be empty"),
        (
            {"start_date_local": datetime.fromisoformat("2026-09-07T07:30:00")},
            "timezone-aware",
        ),
        ({"distance": -1}, "distance"),
        ({"distance": 10**10_000}, "finite non-negative"),
        ({"moving_time": -1}, "moving_time"),
        (
            {"moving_time": 10**100, "elapsed_time": 10**100},
            "supported duration range",
        ),
        ({"elapsed_time": 3_000}, "shorter"),
        ({"perceived_exertion": 11}, "between 0 and 10"),
        (
            {"average_heartrate": 180, "max_heartrate": 170},
            "cannot exceed",
        ),
    ],
    ids=[
        "empty-name",
        "blank-name",
        "empty-sport",
        "blank-sport",
        "empty-gear-id",
        "blank-gear-id",
        "naive-start-date",
        "negative-distance",
        "unrepresentable-distance",
        "negative-moving-time",
        "unrepresentable-duration",
        "moving-exceeds-elapsed",
        "exertion-over-ten",
        "average-heart-rate-over-maximum",
    ],
)
def test_enforces_domain_invariants(changes: dict[str, object], message: str) -> None:
    with pytest.raises(ValueError, match=message):
        replace(activity_model(), **changes)


def test_activity_is_immutable() -> None:
    activity = activity_model()
    attribute_name = "name"

    with pytest.raises(FrozenInstanceError):
        setattr(activity, attribute_name, "Changed")
