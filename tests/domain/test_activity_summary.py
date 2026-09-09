from datetime import timedelta

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
        perceived_exertion=None,
    )

    summary = WeeklyActivitySummary.from_activities([complete, incomplete])

    assert summary.average_heartrate == complete.average_heartrate
    assert summary.average_max_heartrate == complete.max_heartrate
    assert summary.average_perceived_exertion == complete.perceived_exertion
