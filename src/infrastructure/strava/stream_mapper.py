from collections.abc import Mapping, Sequence
from math import isfinite
from typing import cast

from src.domain.activity_stream import ActivityStream, StreamSample


def map_activity_stream(activity_id: int, payload: object) -> ActivityStream:
    """Translate an untrusted Strava stream payload into aligned samples."""
    if not isinstance(payload, Mapping):
        raise TypeError("Strava streams response must be an object.")
    values = cast(Mapping[str, object], payload)
    times = _integer_stream(values, "time")
    distances = _float_stream(values, "distance")
    heart_rates = _integer_stream(values, "heartrate")
    sample_count = max(
        (len(times), len(distances), len(heart_rates)),
        default=0,
    )

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


def _stream_values(payload: Mapping[str, object], key: str) -> Sequence[object]:
    stream = payload.get(key)
    if stream is None:
        return ()
    if not isinstance(stream, Mapping):
        raise TypeError(f"Stream '{key}' must be an object.")
    values = stream.get("data")
    if values is None:
        return ()
    if not isinstance(values, Sequence) or isinstance(values, (str, bytes)):
        raise TypeError(f"Stream '{key}' data must be a sequence.")
    return values


def _integer_stream(payload: Mapping[str, object], key: str) -> tuple[int, ...]:
    values: list[int] = []
    for value in _stream_values(payload, key):
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"Stream '{key}' values must be integers.")
        if value < 0:
            raise ValueError(f"Stream '{key}' values cannot be negative.")
        values.append(value)
    return tuple(values)


def _float_stream(payload: Mapping[str, object], key: str) -> tuple[float, ...]:
    values: list[float] = []
    for value in _stream_values(payload, key):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"Stream '{key}' values must be numeric.")
        numeric_value = float(value)
        if not isfinite(numeric_value) or numeric_value < 0:
            raise ValueError(f"Stream '{key}' values must be finite and non-negative.")
        values.append(numeric_value)
    return tuple(values)


def _value_at[T](values: Sequence[T], index: int) -> T | None:
    return values[index] if index < len(values) else None
