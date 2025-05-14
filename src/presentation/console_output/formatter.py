from datetime import datetime
from typing import Any

from src.interfaces.formatter import IValueFormatter


class ActivityDateFormatter(IValueFormatter):
    def format(self, value: Any) -> str:
        try:
            dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            return str(value)


class ActivityDistanceFormatter(IValueFormatter):
    def format(self, value: Any) -> str:
        try:
            return f"{float(value) / 1000:.2f} km"
        except (ValueError, TypeError):
            return str(value)


class ActivityPaceFormatter(IValueFormatter):
    def format(self, value: Any) -> str:
        try:
            return f"{float(value) * 3.6:.2f} km/h"
        except (ValueError, TypeError):
            return str(value)


class ActivityDurationFormatter(IValueFormatter):
    def format(self, value: Any) -> str:
        try:
            minutes = int(value) // 60
            seconds = int(value) % 60
            return f"{minutes}m {seconds}s"
        except (ValueError, TypeError):
            return str(value)


class ActivityHeartRateFormatter(IValueFormatter):
    def format(self, value: Any) -> str:
        try:
            return f"{int(value)} ppm"
        except (ValueError, TypeError):
            return str(value)


class ActivityCaloriesFormatter(IValueFormatter):
    def format(self, value: Any) -> str:
        try:
            return f"{int(value)} kcal"
        except (ValueError, TypeError):
            return str(value)


class ActivityExertionFormatter(IValueFormatter):
    def format(self, value: Any) -> str:
        try:
            return f"{int(value)} RPE"
        except (ValueError, TypeError):
            return str(value)


class ActivityFormatter:
    def __init__(self) -> None:
        self.formatters = {
            "start_date": ActivityDateFormatter(),
            "start_date_local": ActivityDateFormatter(),
            "distance": ActivityDistanceFormatter(),
            "average_speed": ActivityPaceFormatter(),
            "moving_time": ActivityDurationFormatter(),
            "elapsed_time": ActivityDurationFormatter(),
            "average_heartrate": ActivityHeartRateFormatter(),
            "max_heartrate": ActivityHeartRateFormatter(),
            "calories": ActivityCaloriesFormatter(),
            "perceived_exertion": ActivityExertionFormatter(),
        }

    def format_key(self, key: str) -> str:
        return key.replace("_", " ").title()

    def format_value(self, key: str, value: Any) -> str:
        formatter = self.formatters.get(key)
        if formatter:
            return formatter.format(value)
        return str(value)
