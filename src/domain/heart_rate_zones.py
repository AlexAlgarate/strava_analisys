from dataclasses import dataclass

from src.domain.activity_id import require_activity_id


@dataclass(frozen=True, slots=True)
class HeartRateZone:
    """Time spent in a single heart-rate interval."""

    number: int
    minimum_bpm: int
    maximum_bpm: int | None
    time_seconds: int

    def __post_init__(self) -> None:
        for name, value in (
            ("number", self.number),
            ("minimum", self.minimum_bpm),
            ("time", self.time_seconds),
        ):
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(f"Heart-rate zone {name} must be an integer.")
        if self.maximum_bpm is not None and (
            isinstance(self.maximum_bpm, bool) or not isinstance(self.maximum_bpm, int)
        ):
            raise TypeError("Heart-rate zone maximum must be an integer when provided.")
        if self.number not in range(1, 6):
            raise ValueError("Heart-rate zone number must be between one and five.")
        if self.minimum_bpm < 0:
            raise ValueError("Heart-rate zone minimum cannot be negative.")
        if self.maximum_bpm is not None and self.maximum_bpm <= self.minimum_bpm:
            raise ValueError("Heart-rate zone maximum must exceed its minimum.")
        if self.time_seconds < 0:
            raise ValueError("Heart-rate zone time cannot be negative.")


@dataclass(frozen=True, slots=True)
class HeartRateZones:
    """The five heart-rate zones returned for an activity."""

    activity_id: int
    zones: tuple[HeartRateZone, ...]

    def __post_init__(self) -> None:
        require_activity_id(self.activity_id)
        if not isinstance(self.zones, tuple) or not all(
            isinstance(zone, HeartRateZone) for zone in self.zones
        ):
            raise TypeError("Heart-rate zones must be a tuple of HeartRateZone.")
        if len(self.zones) != 5:
            raise ValueError("An activity must contain exactly five heart-rate zones.")
        if tuple(zone.number for zone in self.zones) != (1, 2, 3, 4, 5):
            raise ValueError("Heart-rate zones must be ordered from one to five.")
        if any(zone.maximum_bpm is None for zone in self.zones[:-1]):
            raise ValueError("Only the final heart-rate zone may be unbounded.")
        if self.zones[-1].maximum_bpm is not None:
            raise ValueError("The final heart-rate zone must be unbounded.")
        if any(
            current.maximum_bpm != following.minimum_bpm
            for current, following in zip(
                self.zones[:-1],
                self.zones[1:],
                strict=True,
            )
        ):
            raise ValueError("Heart-rate zones must form contiguous intervals.")
