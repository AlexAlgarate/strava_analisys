from dataclasses import dataclass
from datetime import datetime
from math import isfinite

from src.domain.activity_id import require_activity_id


@dataclass(frozen=True, slots=True)
class DetailedActivity:
    """Validated activity data used by analysis use cases.

    Distances and speeds retain Strava's native units: metres and metres per
    second. Durations are expressed in seconds.
    """

    id: int
    name: str
    distance: float
    moving_time: int
    elapsed_time: int
    start_date_local: datetime
    sport_type: str
    total_elevation_gain: float = 0.0
    gear_id: str | None = None
    average_heartrate: float | None = None
    max_heartrate: float | None = None
    calories: float | None = None
    perceived_exertion: int | None = None
    average_speed: float | None = None

    def __post_init__(self) -> None:
        require_activity_id(self.id)
        _require_non_empty_text("name", self.name)
        _require_non_empty_text("sport type", self.sport_type)
        _require_aware_datetime(self.start_date_local)
        self._require_non_negative("distance", self.distance)
        self._require_non_negative_integer("moving_time", self.moving_time)
        self._require_non_negative_integer("elapsed_time", self.elapsed_time)
        self._require_non_negative("total_elevation_gain", self.total_elevation_gain)
        if self.elapsed_time < self.moving_time:
            raise ValueError("Elapsed time cannot be shorter than moving time.")

        self._validate_optional_metrics()
        if self.gear_id is not None and not isinstance(self.gear_id, str):
            raise TypeError("Activity gear id must be a string when provided.")
        self._validate_perceived_exertion()
        if (
            self.average_heartrate is not None
            and self.max_heartrate is not None
            and self.average_heartrate > self.max_heartrate
        ):
            raise ValueError("Average heartrate cannot exceed maximum heartrate.")

    def _validate_optional_metrics(self) -> None:
        for name, value in (
            ("average_heartrate", self.average_heartrate),
            ("max_heartrate", self.max_heartrate),
            ("calories", self.calories),
            ("average_speed", self.average_speed),
        ):
            if value is not None:
                self._require_non_negative(name, value)

    def _validate_perceived_exertion(self) -> None:
        if self.perceived_exertion is None:
            return
        if isinstance(self.perceived_exertion, bool) or not isinstance(
            self.perceived_exertion, int
        ):
            raise TypeError("Perceived exertion must be an integer.")
        if not 0 <= self.perceived_exertion <= 10:
            raise ValueError("Perceived exertion must be between 0 and 10.")

    @staticmethod
    def _require_non_negative(name: str, value: object) -> None:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"Activity {name} must be numeric.")
        if not isfinite(value) or value < 0:
            raise ValueError(f"Activity {name} must be a finite non-negative value.")

    @staticmethod
    def _require_non_negative_integer(name: str, value: object) -> None:
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"Activity {name} must be an integer.")
        if value < 0:
            raise ValueError(f"Activity {name} cannot be negative.")


def _require_non_empty_text(name: str, value: object) -> None:
    if not isinstance(value, str):
        raise TypeError(f"Activity {name} must be a string.")
    if not value.strip():
        raise ValueError(f"Activity {name} cannot be empty.")


def _require_aware_datetime(value: object) -> None:
    if not isinstance(value, datetime):
        raise TypeError("Activity start date must be a datetime.")
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("Activity start date must be timezone-aware.")
