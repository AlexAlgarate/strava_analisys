from dataclasses import dataclass
from math import isfinite

from src.domain.activity_id import require_activity_id


@dataclass(frozen=True, slots=True)
class StreamSample:
    """One synchronized sample from an activity stream."""

    elapsed_seconds: int | None
    distance_metres: float | None
    heart_rate_bpm: int | None

    def __post_init__(self) -> None:
        _validate_optional_integer("time", self.elapsed_seconds)
        _validate_optional_float("distance", self.distance_metres)
        _validate_optional_integer("heartrate", self.heart_rate_bpm)
        if (
            self.elapsed_seconds is None
            and self.distance_metres is None
            and self.heart_rate_bpm is None
        ):
            raise ValueError("A stream sample must contain at least one measurement.")


@dataclass(frozen=True, slots=True)
class ActivityStream:
    """Validated stream samples belonging to one Strava activity."""

    activity_id: int
    samples: tuple[StreamSample, ...]

    def __post_init__(self) -> None:
        require_activity_id(self.activity_id)
        if not isinstance(self.samples, tuple) or not all(
            isinstance(sample, StreamSample) for sample in self.samples
        ):
            raise TypeError("Activity stream samples must be a tuple of StreamSample.")


@dataclass(frozen=True, slots=True)
class StreamFetchFailure:
    """A failed activity request retained in a batch result."""

    activity_id: int
    error_type: str
    message: str

    def __post_init__(self) -> None:
        require_activity_id(self.activity_id)
        if not isinstance(self.error_type, str):
            raise TypeError("Stream failure error type must be a string.")
        if not self.error_type.strip():
            raise ValueError("Stream failure error type cannot be empty.")
        if not isinstance(self.message, str):
            raise TypeError("Stream failure message must be a string.")
        if not self.message.strip():
            raise ValueError("Stream failure message cannot be empty.")


@dataclass(frozen=True, slots=True)
class StreamBatch:
    """Successful streams and explicit per-activity failures from one batch."""

    streams: tuple[ActivityStream, ...] = ()
    failures: tuple[StreamFetchFailure, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.streams, tuple) or not all(
            isinstance(stream, ActivityStream) for stream in self.streams
        ):
            raise TypeError("Batch streams must be a tuple of ActivityStream.")
        if not isinstance(self.failures, tuple) or not all(
            isinstance(failure, StreamFetchFailure) for failure in self.failures
        ):
            raise TypeError("Batch failures must be a tuple of StreamFetchFailure.")

        stream_ids = [stream.activity_id for stream in self.streams]
        failure_ids = [failure.activity_id for failure in self.failures]
        if len(stream_ids) != len(set(stream_ids)):
            raise ValueError("A stream batch cannot contain duplicate stream IDs.")
        if len(failure_ids) != len(set(failure_ids)):
            raise ValueError("A stream batch cannot contain duplicate failure IDs.")
        if set(stream_ids).intersection(failure_ids):
            raise ValueError(
                "An activity cannot be both successful and failed in one stream batch."
            )

    @property
    def sample_count(self) -> int:
        return sum(len(stream.samples) for stream in self.streams)

    @property
    def is_partial(self) -> bool:
        return bool(self.streams and self.failures)


def _validate_optional_integer(name: str, value: object) -> None:
    if value is None:
        return
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"Stream sample {name} must be an integer.")
    if value < 0:
        raise ValueError(f"Stream sample {name} cannot be negative.")


def _validate_optional_float(name: str, value: object) -> None:
    if value is None:
        return
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"Stream sample {name} must be numeric.")
    try:
        finite = isfinite(value)
    except OverflowError as error:
        raise ValueError(
            f"Stream sample {name} must be finite and non-negative."
        ) from error
    if not finite or value < 0:
        raise ValueError(f"Stream sample {name} must be finite and non-negative.")
