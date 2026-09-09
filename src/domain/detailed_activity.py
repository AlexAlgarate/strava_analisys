from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from math import isfinite
from types import MappingProxyType
from typing import Self


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
    gear: Mapping[str, object] | None = None

    def __post_init__(self) -> None:
        if isinstance(self.id, bool) or not isinstance(self.id, int):
            raise TypeError("Activity id must be an integer.")
        if self.id <= 0:
            raise ValueError("Activity id must be a positive integer.")
        if not isinstance(self.name, str):
            raise TypeError("Activity name must be a string.")
        if not self.name.strip():
            raise ValueError("Activity name cannot be empty.")
        if not isinstance(self.sport_type, str):
            raise TypeError("Activity sport type must be a string.")
        if not self.sport_type.strip():
            raise ValueError("Activity sport type cannot be empty.")
        if not isinstance(self.start_date_local, datetime):
            raise TypeError("Activity start date must be a datetime.")
        self._require_non_negative("distance", self.distance)
        self._require_non_negative_integer("moving_time", self.moving_time)
        self._require_non_negative_integer("elapsed_time", self.elapsed_time)
        self._require_non_negative("total_elevation_gain", self.total_elevation_gain)
        if self.elapsed_time < self.moving_time:
            raise ValueError("Elapsed time cannot be shorter than moving time.")

        for name, value in (
            ("average_heartrate", self.average_heartrate),
            ("max_heartrate", self.max_heartrate),
            ("calories", self.calories),
            ("average_speed", self.average_speed),
        ):
            if value is not None:
                self._require_non_negative(name, value)
        if self.perceived_exertion is not None and not (
            isinstance(self.perceived_exertion, int)
            and not isinstance(self.perceived_exertion, bool)
            and 0 <= self.perceived_exertion <= 10
        ):
            raise ValueError("Perceived exertion must be between 0 and 10.")
        if (
            self.average_heartrate is not None
            and self.max_heartrate is not None
            and self.average_heartrate > self.max_heartrate
        ):
            raise ValueError("Average heartrate cannot exceed maximum heartrate.")
        if self.gear is not None:
            if not isinstance(self.gear, Mapping):
                raise TypeError("Activity gear must be a mapping.")
            object.__setattr__(self, "gear", MappingProxyType(dict(self.gear)))

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> Self:
        """Create an activity from an untrusted API response."""
        return cls(
            id=_required_int(payload, "id"),
            name=_required_str(payload, "name"),
            distance=_required_number(payload, "distance"),
            moving_time=_required_int(payload, "moving_time"),
            elapsed_time=_required_int(payload, "elapsed_time"),
            start_date_local=_required_datetime(payload, "start_date_local"),
            sport_type=_required_str(payload, "sport_type"),
            total_elevation_gain=_number_or_default(
                payload, "total_elevation_gain", default=0.0
            ),
            gear_id=_optional_str(payload, "gear_id"),
            average_heartrate=_optional_number(payload, "average_heartrate"),
            max_heartrate=_optional_number(payload, "max_heartrate"),
            calories=_optional_number(payload, "calories"),
            perceived_exertion=_optional_int(payload, "perceived_exertion"),
            average_speed=_optional_number(payload, "average_speed"),
            gear=_optional_mapping(payload, "gear"),
        )

    def as_dict(self) -> dict[str, object]:
        """Return a presentation-friendly representation."""
        values: dict[str, object] = {
            "id": self.id,
            "name": self.name,
            "distance": self.distance,
            "moving_time": self.moving_time,
            "elapsed_time": self.elapsed_time,
            "start_date_local": self.start_date_local.isoformat(),
            "sport_type": self.sport_type,
            "total_elevation_gain": self.total_elevation_gain,
        }
        optional_values = {
            "gear_id": self.gear_id,
            "average_heartrate": self.average_heartrate,
            "max_heartrate": self.max_heartrate,
            "calories": self.calories,
            "perceived_exertion": self.perceived_exertion,
            "average_speed": self.average_speed,
            "gear": dict(self.gear) if self.gear is not None else None,
        }
        values.update(
            {key: value for key, value in optional_values.items() if value is not None}
        )
        return values

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


def _required_str(payload: Mapping[str, object], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str):
        raise TypeError(f"Activity {key} must be a string.")
    return value


def _optional_str(payload: Mapping[str, object], key: str) -> str | None:
    value = payload.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise TypeError(f"Activity {key} must be a string when provided.")
    return value


def _required_int(payload: Mapping[str, object], key: str) -> int:
    value = payload.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"Activity {key} must be an integer.")
    return value


def _optional_int(payload: Mapping[str, object], key: str) -> int | None:
    value = payload.get(key)
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"Activity {key} must be an integer when provided.")
    return value


def _required_number(payload: Mapping[str, object], key: str) -> float:
    value = payload.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"Activity {key} must be numeric.")
    return float(value)


def _optional_number(
    payload: Mapping[str, object],
    key: str,
    *,
    default: float | None = None,
) -> float | None:
    value = payload.get(key)
    if value is None:
        return default
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"Activity {key} must be numeric when provided.")
    return float(value)


def _number_or_default(
    payload: Mapping[str, object], key: str, *, default: float
) -> float:
    value = _optional_number(payload, key)
    return default if value is None else value


def _required_datetime(payload: Mapping[str, object], key: str) -> datetime:
    value = _required_str(payload, key)
    try:
        return datetime.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"Activity {key} must be an ISO 8601 datetime.") from exc


def _optional_mapping(
    payload: Mapping[str, object], key: str
) -> Mapping[str, object] | None:
    value = payload.get(key)
    if value is None:
        return None
    if not isinstance(value, Mapping) or not all(
        isinstance(item_key, str) for item_key in value
    ):
        raise TypeError(f"Activity {key} must be an object when provided.")
    return {str(item_key): item_value for item_key, item_value in value.items()}
