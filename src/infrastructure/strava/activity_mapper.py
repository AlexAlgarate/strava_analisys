from collections.abc import Mapping
from datetime import datetime
from typing import cast

from src.domain.detailed_activity import DetailedActivity


def map_activity_list(payload: object) -> list[DetailedActivity]:
    """Translate an untrusted Strava activity collection into domain objects."""
    if not isinstance(payload, list):
        raise TypeError("Strava activities response must be a list.")
    return [map_activity(item) for item in payload]


def map_activity(payload: object) -> DetailedActivity:
    """Translate one untrusted Strava activity payload into the domain."""
    values = _string_mapping(payload)
    return DetailedActivity(
        id=_required_int(values, "id"),
        name=_required_str(values, "name"),
        distance=_required_number(values, "distance"),
        moving_time=_required_int(values, "moving_time"),
        elapsed_time=_required_int(values, "elapsed_time"),
        start_date_local=_required_datetime(values, "start_date_local"),
        sport_type=_required_str(values, "sport_type"),
        total_elevation_gain=_number_or_default(
            values,
            "total_elevation_gain",
            default=0.0,
        ),
        gear_id=_optional_str(values, "gear_id"),
        average_heartrate=_optional_number(values, "average_heartrate"),
        max_heartrate=_optional_number(values, "max_heartrate"),
        calories=_optional_number(values, "calories"),
        perceived_exertion=_optional_int(values, "perceived_exertion"),
        average_speed=_optional_number(values, "average_speed"),
    )


def _string_mapping(payload: object) -> Mapping[str, object]:
    if not isinstance(payload, dict) or not all(
        isinstance(key, str) for key in payload
    ):
        raise TypeError("A Strava activity must be an object with string keys.")
    return cast(dict[str, object], payload)


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
    payload: Mapping[str, object],
    key: str,
    *,
    default: float,
) -> float:
    value = _optional_number(payload, key)
    return default if value is None else value


def _required_datetime(payload: Mapping[str, object], key: str) -> datetime:
    value = _required_str(payload, key)
    try:
        return datetime.fromisoformat(value)
    except ValueError as error:
        raise ValueError(f"Activity {key} must be an ISO 8601 datetime.") from error
