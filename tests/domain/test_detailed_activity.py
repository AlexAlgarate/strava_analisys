from dataclasses import FrozenInstanceError, replace
from datetime import datetime
from typing import cast

import pytest

from tests.factories import activity_model


def test_keeps_valid_activity_values() -> None:
    activity = activity_model(gear_id="g1")

    assert activity.id == 1
    assert activity.start_date_local == datetime.fromisoformat("2026-09-07T07:30:00")
    assert activity.distance == 10_000
    assert activity.gear_id == "g1"


@pytest.mark.parametrize(
    ("changes", "error_type"),
    [
        ({"id": True}, TypeError),
        ({"name": cast(str, 42)}, TypeError),
        ({"sport_type": cast(str, 42)}, TypeError),
        ({"distance": cast(float, "far")}, TypeError),
        ({"moving_time": cast(int, 1.5)}, TypeError),
        ({"start_date_local": cast(datetime, "not-a-date")}, TypeError),
        ({"gear_id": cast(str, 42)}, TypeError),
        ({"perceived_exertion": cast(int, 1.5)}, TypeError),
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
        ({"sport_type": ""}, "sport type cannot be empty"),
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
    with pytest.raises(ValueError, match=message):
        replace(activity_model(), **changes)


def test_activity_is_immutable() -> None:
    activity = activity_model()

    with pytest.raises(FrozenInstanceError):
        activity.name = "Changed"  # type: ignore[misc]
