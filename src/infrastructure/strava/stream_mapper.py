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
    available_streams = tuple(
        stream for stream in (times, distances, heart_rates) if stream is not None
    )
    stream_lengths = {len(stream) for stream in available_streams}
    if len(stream_lengths) > 1:
        raise ValueError("Present Strava streams must contain the same sample count.")
    sample_count = next(iter(stream_lengths), 0)

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


def _stream_values(payload: Mapping[str, object], key: str) -> Sequence[object] | None:
    stream = payload.get(key)
    if stream is None:
        return None
    if not isinstance(stream, Mapping):
        raise TypeError(f"Stream '{key}' must be an object.")
    values = stream.get("data")
    if not isinstance(values, Sequence) or isinstance(values, (str, bytes)):
        raise TypeError(f"Stream '{key}' data must be a sequence.")
    return values


def _integer_stream(payload: Mapping[str, object], key: str) -> tuple[int, ...] | None:
    stream_values = _stream_values(payload, key)
    if stream_values is None:
        return None
    values: list[int] = []
    for value in stream_values:
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"Stream '{key}' values must be integers.")
        if value < 0:
            raise ValueError(f"Stream '{key}' values cannot be negative.")
        values.append(value)
    return tuple(values)


def _float_stream(payload: Mapping[str, object], key: str) -> tuple[float, ...] | None:
    stream_values = _stream_values(payload, key)
    if stream_values is None:
        return None
    values: list[float] = []
    for value in stream_values:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"Stream '{key}' values must be numeric.")
        try:
            numeric_value = float(value)
        except OverflowError as error:
            raise ValueError(
                f"Stream '{key}' values must be finite and non-negative."
            ) from error
        if not isfinite(numeric_value) or numeric_value < 0:
            raise ValueError(f"Stream '{key}' values must be finite and non-negative.")
        values.append(numeric_value)
    return tuple(values)


def _value_at[T](values: Sequence[T] | None, index: int) -> T | None:
    return None if values is None else values[index]
