from datetime import timedelta
from typing import Any

from src.core.activities.summary.interfaces import IMetricCalculator


class DistanceCalculator(IMetricCalculator):
    def calculate(self, activities: list[dict[str, Any]]) -> dict[str, Any]:
        total_distance = sum(activity.get("distance", 0) for activity in activities)
        return {"total_distance": round(total_distance / 1000, 2)}  # Convert to km


class MovingTimeCalculator(IMetricCalculator):
    def calculate(self, activities: list[dict[str, Any]]) -> dict[str, Any]:
        total_moving_time = sum(
            activity.get("moving_time", 0) for activity in activities
        )
        formatted_time = str(timedelta(seconds=total_moving_time))
        return {"total_moving_time": formatted_time}


class ElevationGainCalculator(IMetricCalculator):
    def calculate(self, activities: list[dict[str, Any]]) -> dict[str, Any]:
        total_elevation = sum(
            activity.get("total_elevation_gain", 0) for activity in activities
        )
        return {"total_elevation_gain": round(total_elevation, 1)}


class HeartRateCalculator(IMetricCalculator):
    def calculate(self, activities: list[dict[str, Any]]) -> dict[str, Any]:
        total_hr = 0
        total_max_hr = 0
        activities_with_hr = 0
        activities_with_max_hr = 0

        for activity in activities:
            if "average_heartrate" in activity:
                total_hr += activity["average_heartrate"]
                activities_with_hr += 1
            if "max_heartrate" in activity:
                total_max_hr += activity["max_heartrate"]
                activities_with_max_hr += 1

        avg_hr = (
            round(total_hr / activities_with_hr, 1) if activities_with_hr > 0 else 0
        )
        avg_max_hr = (
            round(total_max_hr / activities_with_max_hr, 1)
            if activities_with_max_hr > 0
            else 0
        )

        return {"avg_heartrate": avg_hr, "avg_max_heartrate": avg_max_hr}


class CaloriesCalculator(IMetricCalculator):
    def calculate(self, activities: list[dict[str, Any]]) -> dict[str, Any]:
        total_calories = sum(activity.get("calories", 0) for activity in activities)
        return {"total_calories": round(total_calories, 1)}


class PerceivedExertionCalculator(IMetricCalculator):
    def calculate(self, activities: list[dict[str, Any]]) -> dict[str, Any]:
        total_pe = 0
        activities_with_pe = 0

        for activity in activities:
            if "perceived_exertion" in activity:
                total_pe += activity["perceived_exertion"]
                activities_with_pe += 1

        avg_pe = (
            round(total_pe / activities_with_pe, 1) if activities_with_pe > 0 else 0
        )
        return {"avg_perceived_exertion": avg_pe}
