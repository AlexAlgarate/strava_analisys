from typing import Any

from src.core.activities.summary.ports import SummaryData


class ActivitySummaryBuilder:
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self._summary: dict[str, Any] = {}

    def add_distance(self, value: float) -> None:
        self._summary["total_distance"] = value

    def add_moving_time(self, value: str) -> None:
        self._summary["total_moving_time"] = value

    def add_elevation_gain(self, value: float) -> None:
        self._summary["total_elevation_gain"] = value

    def add_heart_rate_metrics(self, avg: float, max_avg: float) -> None:
        self._summary["avg_heartrate"] = avg
        self._summary["avg_max_heartrate"] = max_avg

    def add_calories(self, value: float) -> None:
        self._summary["total_calories"] = value

    def add_perceived_exertion(self, value: float) -> None:
        self._summary["avg_perceived_exertion"] = value

    def get_summary(self) -> SummaryData:
        return self._summary.copy()
