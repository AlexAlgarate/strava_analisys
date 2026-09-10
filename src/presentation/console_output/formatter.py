from datetime import datetime
from typing import Protocol

type NumericInput = str | int | float


def _require_numeric_input(value: object) -> NumericInput:
    if not isinstance(value, bool) and isinstance(value, (str, int, float)):
        return value
    raise TypeError("Value must be numeric or a numeric string.")


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
    def format(self, value: object) -> str:
        try:
            return f"{float(_require_numeric_input(value)) / 1000:.2f} km"
        except (ValueError, TypeError):
            return str(value)


class ActivitySpeedFormatter:
    def format(self, value: object) -> str:
        try:
            return f"{float(_require_numeric_input(value)) * 3.6:.2f} km/h"
        except (ValueError, TypeError):
            return str(value)


class ActivityDurationFormatter:
    def format(self, value: object) -> str:
        try:
            numeric_value = _require_numeric_input(value)
            minutes = int(numeric_value) // 60
            seconds = int(numeric_value) % 60
            return f"{minutes}m {seconds}s"
        except (ValueError, TypeError):
            return str(value)


class ActivityHeartRateFormatter:
    def format(self, value: object) -> str:
        try:
            return f"{int(_require_numeric_input(value))} ppm"
        except (ValueError, TypeError):
            return str(value)


class ActivityCaloriesFormatter:
    def format(self, value: object) -> str:
        try:
            return f"{int(_require_numeric_input(value))} kcal"
        except (ValueError, TypeError):
            return str(value)


class ActivityExertionFormatter:
    def format(self, value: object) -> str:
        try:
            return f"{int(_require_numeric_input(value))} RPE"
        except (ValueError, TypeError):
            return str(value)


class ActivityFormatter:
    def __init__(self) -> None:
        self.formatters: dict[str, ValueFormatter] = {
            "start_date": ActivityDateFormatter(),
            "start_date_local": ActivityDateFormatter(),
            "distance": ActivityDistanceFormatter(),
            "average_speed": ActivitySpeedFormatter(),
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
