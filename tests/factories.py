from datetime import datetime

from src.domain.activity_stream import ActivityStream, StreamSample
from src.domain.detailed_activity import DetailedActivity
from src.domain.heart_rate_zones import HeartRateZone, HeartRateZones


def activity_model(
    activity_id: int = 1,
    name: str = "Morning Run",
    *,
    distance: float = 10_000,
    moving_time: int = 3_600,
    elapsed_time: int = 3_900,
    start_date_local: datetime | None = None,
    sport_type: str = "Run",
    total_elevation_gain: float = 120,
    gear_id: str | None = None,
    average_heartrate: float | None = 145,
    max_heartrate: float | None = 172,
    calories: float | None = 650,
    perceived_exertion: int | None = 6,
    average_speed: float | None = 2.78,
) -> DetailedActivity:
    return DetailedActivity(
        id=activity_id,
        name=name,
        distance=distance,
        moving_time=moving_time,
        elapsed_time=elapsed_time,
        start_date_local=start_date_local
        or datetime.fromisoformat("2026-09-07T07:30:00"),
        sport_type=sport_type,
        total_elevation_gain=total_elevation_gain,
        gear_id=gear_id,
        average_heartrate=average_heartrate,
        max_heartrate=max_heartrate,
        calories=calories,
        perceived_exertion=perceived_exertion,
        average_speed=average_speed,
    )


def activity_payload(
    activity_id: int = 1,
    name: str = "Morning Run",
    **overrides: object,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "id": activity_id,
        "name": name,
        "distance": 10_000,
        "moving_time": 3_600,
        "elapsed_time": 3_900,
        "start_date_local": "2026-09-07T07:30:00",
        "sport_type": "Run",
        "total_elevation_gain": 120,
        "average_heartrate": 145,
        "max_heartrate": 172,
        "calories": 650,
        "perceived_exertion": 6,
        "average_speed": 2.78,
    }
    payload.update(overrides)
    return payload


def activity_stream(
    activity_id: int = 1,
    *,
    times: tuple[int, ...] = (0, 1, 2),
    distances: tuple[float, ...] = (0.0, 10.5, 20.5),
    heart_rates: tuple[int, ...] = (120, 125, 130),
) -> ActivityStream:
    sample_count = max(len(times), len(distances), len(heart_rates))
    return ActivityStream(
        activity_id=activity_id,
        samples=tuple(
            StreamSample(
                elapsed_seconds=_value_at(times, index),
                distance_metres=_value_at(distances, index),
                heart_rate_bpm=_value_at(heart_rates, index),
            )
            for index in range(sample_count)
        ),
    )


def heart_rate_zones(activity_id: int = 1) -> HeartRateZones:
    values = (
        (0, 120, 300),
        (120, 140, 600),
        (140, 160, 900),
        (160, 180, 400),
        (180, -1, 120),
    )
    return HeartRateZones(
        activity_id=activity_id,
        zones=tuple(
            HeartRateZone(
                number=number,
                minimum_bpm=minimum,
                maximum_bpm=maximum,
                time_seconds=seconds,
            )
            for number, (minimum, maximum, seconds) in enumerate(values, start=1)
        ),
    )


def stream_payload(
    *,
    times: list[int] | None = None,
    distances: list[int | float] | None = None,
    heart_rates: list[int] | None = None,
) -> dict[str, object]:
    return {
        "time": {"data": times if times is not None else [0, 1, 2]},
        "distance": {"data": distances if distances is not None else [0, 10.5, 20.5]},
        "heartrate": {
            "data": heart_rates if heart_rates is not None else [120, 125, 130]
        },
    }


def zones_payload() -> dict[str, object]:
    return {
        "distribution_buckets": [
            {"min": 0, "max": 120, "time": 300},
            {"min": 120, "max": 140, "time": 600},
            {"min": 140, "max": 160, "time": 900},
            {"min": 160, "max": 180, "time": 400},
            {"min": 180, "max": -1, "time": 120},
        ]
    }


def _value_at[T](values: tuple[T, ...], index: int) -> T | None:
    return values[index] if index < len(values) else None
