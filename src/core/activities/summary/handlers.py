from typing import Any, Dict, List

from src.core.activities.summary.interfaces import (
    IActivityDataLoader,
    IActivitySummaryBuilder,
    IActivitySummaryPresenter,
)


class ActivitySummaryBuilder(IActivitySummaryBuilder):
    def __init__(self):
        self.reset()

    def reset(self) -> None:
        self._summary = {}

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

    def get_summary(self) -> Dict[str, Any]:
        return self._summary.copy()


class JsonActivityLoader(IActivityDataLoader):
    def __init__(self, file_path: str):
        self.file_path = file_path

    def load_activities(self) -> List[Dict[str, Any]]:
        import json

        with open(self.file_path, "r", encoding="utf-8") as f:
            return json.load(f)


class ConsolePresenter(IActivitySummaryPresenter):
    def present_weekly_report(self, summary: Dict[str, Any]) -> None:
        print("\n---- Weekly Summary ----")
        print(f"Total Distance: {summary['total_distance']} km")
        print(f"Total Moving Time: {summary['total_moving_time']}")
        print(f"Total Elevation Gain: {summary['total_elevation_gain']} m")
        print(f"Average Heart Rate: {summary['avg_heartrate']} bpm")
        print(f"Average Max Heart Rate: {summary['avg_max_heartrate']} bpm")
        print(f"Total Calories: {summary['total_calories']} kcal")
        print(f"Average Perceived Exertion: {summary['avg_perceived_exertion']}")

    def present_weekly_report_by_sport(self, summary: Dict[str, Any]) -> None:
        print("\n---- Weekly Summary By Sport----")
        print(f"Total Distance: {summary['total_distance']} km")
        print(f"Total Moving Time: {summary['total_moving_time']}")
        print(f"Total Elevation Gain: {summary['total_elevation_gain']} m")
        print(f"Average Heart Rate: {summary['avg_heartrate']} bpm")
        print(f"Average Max Heart Rate: {summary['avg_max_heartrate']} bpm")
        print(f"Total Calories: {summary['total_calories']} kcal")
        print(f"Average Perceived Exertion: {summary['avg_perceived_exertion']}")
