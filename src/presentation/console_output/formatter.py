from typing import Protocol

type NumericInput = str | int | float


def _require_numeric_input(value: object) -> NumericInput:
    if not isinstance(value, bool) and isinstance(value, (str, int, float)):
        return value
    raise TypeError("Value must be numeric or a numeric string.")


class ValueFormatter(Protocol):
    def format(self, value: object) -> str: ...


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
            return f"{int(_require_numeric_input(value))} bpm"
        except (ValueError, TypeError):
            return str(value)


class ActivityCaloriesFormatter:
    def format(self, value: object) -> str:
        try:
            return f"{int(_require_numeric_input(value))} kcal"
        except (ValueError, TypeError):
            return str(value)


class ActivityFormatter:
    def __init__(self) -> None:
        self._distance = ActivityDistanceFormatter()
        self._speed = ActivitySpeedFormatter()
        self._duration = ActivityDurationFormatter()
        self._heart_rate = ActivityHeartRateFormatter()
        self._calories = ActivityCaloriesFormatter()

    def format_distance(self, value: object) -> str:
        return self._distance.format(value)

    def format_speed(self, value: object) -> str:
        return self._speed.format(value)

    def format_duration(self, value: object) -> str:
        return self._duration.format(value)

    def format_heart_rate(self, value: object) -> str:
        return self._heart_rate.format(value)

    def format_calories(self, value: object) -> str:
        return self._calories.format(value)
