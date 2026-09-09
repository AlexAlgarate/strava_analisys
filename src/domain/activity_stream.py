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

@dataclass(frozen=True, slots=True)
class ActivityStream:
    """Validated stream samples belonging to one Strava activity."""

    activity_id: int
    samples: tuple[StreamSample, ...]

    def __post_init__(self) -> None:
        require_activity_id(self.activity_id)


@dataclass(frozen=True, slots=True)
class StreamFetchFailure:
    """A failed activity request retained in a batch result."""

    activity_id: int
    error_type: str
    message: str

    def __post_init__(self) -> None:
        require_activity_id(self.activity_id)
        if not self.error_type:
            raise ValueError("Stream failure error type cannot be empty.")
        if not self.message:
            raise ValueError("Stream failure message cannot be empty.")


@dataclass(frozen=True, slots=True)
class StreamBatch:
    """Successful streams and explicit per-activity failures from one batch."""

    streams: tuple[ActivityStream, ...] = ()
    failures: tuple[StreamFetchFailure, ...] = ()

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
    if not isfinite(value) or value < 0:
        raise ValueError(f"Stream sample {name} must be finite and non-negative.")
