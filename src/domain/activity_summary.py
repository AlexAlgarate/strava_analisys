from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import timedelta
from math import isfinite
from statistics import fmean

from src.domain.detailed_activity import DetailedActivity


@dataclass(frozen=True, slots=True)
class WeeklyActivitySummary:
    """Aggregate metrics for a collection of activities."""

    activity_count: int
    total_distance_km: float
    total_moving_time: timedelta
    total_elevation_gain: float
    average_heartrate: float | None
    average_max_heartrate: float | None
    total_calories: float | None
    average_perceived_exertion: float | None

    def __post_init__(self) -> None:
        if isinstance(self.activity_count, bool) or not isinstance(
            self.activity_count, int
        ):
            raise TypeError("Summary activity count must be an integer.")
        if self.activity_count < 0:
            raise ValueError("Summary activity count cannot be negative.")
        if not isinstance(self.total_moving_time, timedelta):
            raise TypeError("Summary moving time must be a timedelta.")
        if self.total_moving_time < timedelta():
            raise ValueError("Summary moving time cannot be negative.")

        _require_non_negative("distance", self.total_distance_km)
        _require_non_negative("elevation gain", self.total_elevation_gain)
        for name, value in (
            ("average heart rate", self.average_heartrate),
            ("average maximum heart rate", self.average_max_heartrate),
            ("calories", self.total_calories),
            ("average perceived exertion", self.average_perceived_exertion),
        ):
            if value is not None:
                _require_non_negative(name, value)
        if (
            self.average_perceived_exertion is not None
            and self.average_perceived_exertion > 10
        ):
            raise ValueError("Summary average perceived exertion cannot exceed ten.")

    @classmethod
    def from_activities(
        cls, activities: Sequence[DetailedActivity]
    ) -> "WeeklyActivitySummary":
        activity_ids = [activity.id for activity in activities]
        if len(activity_ids) != len(set(activity_ids)):
            raise ValueError("Activities in a weekly summary must have unique IDs.")

        return cls(
            activity_count=len(activities),
            total_distance_km=round(
                sum(activity.distance for activity in activities) / 1000,
                2,
            ),
            total_moving_time=_total_moving_time(activities),
            total_elevation_gain=round(
                sum(activity.total_elevation_gain for activity in activities),
                1,
            ),
            average_heartrate=_average(
                activity.average_heartrate for activity in activities
            ),
            average_max_heartrate=_average(
                activity.max_heartrate for activity in activities
            ),
            total_calories=_complete_calorie_total(activities),
            average_perceived_exertion=_average(
                activity.perceived_exertion for activity in activities
            ),
        )


def _average(values: Iterable[float | int | None]) -> float | None:
    present_values = [value for value in values if value is not None]
    return round(fmean(present_values), 1) if present_values else None


def _complete_calorie_total(
    activities: Sequence[DetailedActivity],
) -> float | None:
    values = [activity.calories for activity in activities]
    if any(value is None for value in values):
        return None
    return round(sum(value for value in values if value is not None), 1)


def _total_moving_time(activities: Sequence[DetailedActivity]) -> timedelta:
    total_seconds = sum(activity.moving_time for activity in activities)
    try:
        return timedelta(seconds=total_seconds)
    except OverflowError as error:
        raise ValueError("Summary moving time exceeds the supported range.") from error


def _require_non_negative(name: str, value: object) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"Summary {name} must be numeric.")
    try:
        finite = isfinite(value)
    except OverflowError as error:
        raise ValueError(f"Summary {name} must be finite and non-negative.") from error
    if not finite or value < 0:
        raise ValueError(f"Summary {name} must be finite and non-negative.")
