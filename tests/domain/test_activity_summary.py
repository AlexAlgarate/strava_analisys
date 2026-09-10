from dataclasses import replace
from datetime import timedelta

import pytest

from src.domain.activity_summary import WeeklyActivitySummary
from tests.factories import activity_model


def test_calculates_weekly_summary_from_domain_activities() -> None:
    activities = [
        activity_model(),
        activity_model(
            2,
            "Evening Ride",
            distance=20_555,
            moving_time=1_800,
            elapsed_time=2_000,
            total_elevation_gain=80.56,
            average_heartrate=135,
            max_heartrate=165,
            calories=400.25,
            perceived_exertion=4,
            sport_type="Ride",
        ),
    ]

    summary = WeeklyActivitySummary.from_activities(activities)

    assert summary.activity_count == 2
    assert summary.total_distance_km == 30.55
    assert summary.total_moving_time == timedelta(hours=1, minutes=30)
    assert summary.total_elevation_gain == 200.6
    assert summary.average_heartrate == 140.0
    assert summary.average_max_heartrate == 168.5
    assert summary.total_calories == 1050.2
    assert summary.average_perceived_exertion == 5.0


def test_empty_week_has_zero_totals_and_unknown_averages() -> None:
    summary = WeeklyActivitySummary.from_activities([])

    assert summary.activity_count == 0
    assert summary.total_distance_km == 0
    assert summary.total_moving_time == timedelta()
    assert summary.total_elevation_gain == 0
    assert summary.average_heartrate is None
    assert summary.average_max_heartrate is None
    assert summary.total_calories == 0
    assert summary.average_perceived_exertion is None


def test_missing_optional_metrics_do_not_count_as_zero_in_averages() -> None:
    complete = activity_model()
    incomplete = activity_model(
        2,
        average_heartrate=None,
        max_heartrate=None,
        calories=None,
        perceived_exertion=None,
    )

    summary = WeeklyActivitySummary.from_activities([complete, incomplete])

    assert summary.average_heartrate == complete.average_heartrate
    assert summary.average_max_heartrate == complete.max_heartrate
    assert summary.total_calories is None
    assert summary.average_perceived_exertion == complete.perceived_exertion


def test_rejects_duplicate_activity_ids() -> None:
    activity = activity_model()

    with pytest.raises(ValueError, match="must have unique IDs"):
        WeeklyActivitySummary.from_activities([activity, activity])


def test_rejects_a_total_duration_that_cannot_be_represented() -> None:
    maximum_seconds = timedelta.max.days * 86_400 + timedelta.max.seconds
    activities = [
        activity_model(moving_time=maximum_seconds, elapsed_time=maximum_seconds),
        activity_model(
            2,
            moving_time=maximum_seconds,
            elapsed_time=maximum_seconds,
        ),
    ]

    with pytest.raises(ValueError, match="moving time exceeds") as error:
        WeeklyActivitySummary.from_activities(activities)

    assert isinstance(error.value.__cause__, OverflowError)


@pytest.mark.parametrize(
    ("changes", "error_type", "message"),
    [
        ({"activity_count": True}, TypeError, "count must be an integer"),
        ({"activity_count": -1}, ValueError, "count cannot be negative"),
        ({"total_distance_km": float("nan")}, ValueError, "finite"),
        ({"total_distance_km": 10**10_000}, ValueError, "finite"),
        ({"total_moving_time": timedelta(seconds=-1)}, ValueError, "negative"),
        ({"total_calories": -1}, ValueError, "non-negative"),
        (
            {"average_perceived_exertion": 11},
            ValueError,
            "cannot exceed ten",
        ),
    ],
    ids=[
        "boolean-count",
        "negative-count",
        "non-finite-distance",
        "unrepresentable-distance",
        "negative-moving-time",
        "negative-calories",
        "exertion-over-ten",
    ],
)
def test_summary_rejects_invalid_aggregate_values(
    changes: dict[str, object],
    error_type: type[Exception],
    message: str,
) -> None:
    summary = WeeklyActivitySummary.from_activities([])

    with pytest.raises(error_type, match=message):
        replace(summary, **changes)  # type: ignore[arg-type]
