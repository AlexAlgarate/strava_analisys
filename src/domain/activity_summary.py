from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import timedelta
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
    total_calories: float
    average_perceived_exertion: float | None

    @classmethod
    def from_activities(
        cls, activities: Sequence[DetailedActivity]
    ) -> "WeeklyActivitySummary":
        return cls(
            activity_count=len(activities),
            total_distance_km=round(
                sum(activity.distance for activity in activities) / 1000,
                2,
            ),
            total_moving_time=timedelta(
                seconds=sum(activity.moving_time for activity in activities)
            ),
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
            total_calories=round(
                sum(activity.calories or 0 for activity in activities),
                1,
            ),
            average_perceived_exertion=_average(
                activity.perceived_exertion for activity in activities
            ),
        )


def _average(values: Iterable[float | int | None]) -> float | None:
    present_values = [value for value in values if value is not None]
    return round(fmean(present_values), 1) if present_values else None
