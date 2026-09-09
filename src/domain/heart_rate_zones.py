from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Self, cast


@dataclass(frozen=True, slots=True)
class HeartRateZone:
    """Time spent in a single heart-rate interval."""

    number: int
    minimum_bpm: int
    maximum_bpm: int
    time_seconds: int

    def __post_init__(self) -> None:
        for name, value in (
            ("number", self.number),
            ("minimum", self.minimum_bpm),
            ("maximum", self.maximum_bpm),
            ("time", self.time_seconds),
        ):
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(f"Heart-rate zone {name} must be an integer.")
        if self.number not in range(1, 6):
            raise ValueError("Heart-rate zone number must be between one and five.")
        if self.minimum_bpm < 0:
            raise ValueError("Heart-rate zone minimum cannot be negative.")
        if self.maximum_bpm != -1 and self.maximum_bpm < self.minimum_bpm:
            raise ValueError(
                "Heart-rate zone maximum must exceed its minimum or be -1."
            )
        if self.time_seconds < 0:
            raise ValueError("Heart-rate zone time cannot be negative.")

    @classmethod
    def from_mapping(cls, number: int, payload: Mapping[str, object]) -> Self:
        return cls(
            number=number,
            minimum_bpm=_required_int(payload, "min"),
            maximum_bpm=_required_int(payload, "max"),
            time_seconds=_required_int(payload, "time"),
        )

    def as_dict(self) -> dict[str, int]:
        return {
            "min": self.minimum_bpm,
            "max": self.maximum_bpm,
            "time": self.time_seconds,
        }


@dataclass(frozen=True, slots=True)
class HeartRateZones:
    """The five heart-rate zones returned for an activity."""

    activity_id: int
    zones: tuple[HeartRateZone, ...]

    def __post_init__(self) -> None:
        if isinstance(self.activity_id, bool) or not isinstance(self.activity_id, int):
            raise TypeError("Activity id must be an integer.")
        if self.activity_id <= 0:
            raise ValueError("Activity id must be a positive integer.")
        if len(self.zones) != 5:
            raise ValueError("Strava must return exactly five heart-rate zones.")

    @classmethod
    def from_api_response(cls, activity_id: int, payload: object) -> Self:
        zone_payload = _heart_rate_zone_payload(payload)
        buckets = zone_payload.get("distribution_buckets")
        if buckets is None:
            raise ValueError("The activity does not have heartrate information.")
        if not isinstance(buckets, Sequence) or isinstance(buckets, (str, bytes)):
            raise TypeError("Strava zone buckets must be a sequence.")
        if len(buckets) != 5:
            raise ValueError("Strava must return exactly five heart-rate zones.")

        mappings: list[Mapping[str, object]] = []
        for bucket in cast(Sequence[object], buckets):
            if not isinstance(bucket, Mapping):
                raise TypeError("Each Strava zone bucket must be an object.")
            mappings.append(cast(Mapping[str, object], bucket))

        return cls(
            activity_id=activity_id,
            zones=tuple(
                HeartRateZone.from_mapping(number, bucket)
                for number, bucket in enumerate(mappings, start=1)
            ),
        )

    def as_dict(self) -> dict[str, dict[str, int]]:
        return {f"Zone_{zone.number}": zone.as_dict() for zone in self.zones}


def _heart_rate_zone_payload(payload: object) -> Mapping[str, object]:
    if isinstance(payload, Mapping):
        return cast(Mapping[str, object], payload)
    if not isinstance(payload, Sequence) or isinstance(payload, (str, bytes)):
        raise TypeError("Strava zones response must be an object or a sequence.")

    candidates = [item for item in payload if isinstance(item, Mapping)]
    for candidate in candidates:
        if candidate.get("type") == "heartrate":
            return cast(Mapping[str, object], candidate)
    for candidate in candidates:
        if "distribution_buckets" in candidate:
            return cast(Mapping[str, object], candidate)
    raise ValueError("The activity does not have heartrate information.")


def _required_int(payload: Mapping[str, object], key: str) -> int:
    value = payload.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"Heart-rate zone {key} must be an integer.")
    return value
