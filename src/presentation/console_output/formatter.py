from datetime import datetime
from typing import Any, Protocol


class ValueFormatter(Protocol):
    def format(self, value: object) -> str: ...


class ActivityDateFormatter:
    def format(self, value: object) -> str:
        try:
            dt = datetime.fromisoformat(str(value))
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            return str(value)


class ActivityDistanceFormatter:
    def format(self, value: Any) -> str:
        try:
            return f"{float(value) / 1000:.2f} km"
        except (ValueError, TypeError):
            return str(value)


class ActivityPaceFormatter:
    def format(self, value: Any) -> str:
        try:
            return f"{float(value) * 3.6:.2f} km/h"
        except (ValueError, TypeError):
            return str(value)


class ActivityDurationFormatter:
    def format(self, value: Any) -> str:
        try:
            minutes = int(value) // 60
            seconds = int(value) % 60
            return f"{minutes}m {seconds}s"
        except (ValueError, TypeError):
            return str(value)


class ActivityHeartRateFormatter:
    def format(self, value: Any) -> str:
        try:
            return f"{int(value)} ppm"
        except (ValueError, TypeError):
            return str(value)


class ActivityCaloriesFormatter:
    def format(self, value: Any) -> str:
        try:
            return f"{int(value)} kcal"
        except (ValueError, TypeError):
            return str(value)


class ActivityExertionFormatter:
    def format(self, value: Any) -> str:
        try:
            return f"{int(value)} RPE"
        except (ValueError, TypeError):
            return str(value)


class ActivityFormatter:
    def __init__(self) -> None:
        self.formatters: dict[str, ValueFormatter] = {
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

    def format_value(self, key: str, value: object) -> str:
        formatter = self.formatters.get(key)
        if formatter:
            return formatter.format(value)
        return str(value)
