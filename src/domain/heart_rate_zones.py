from dataclasses import dataclass

from src.domain.activity_id import require_activity_id


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


@dataclass(frozen=True, slots=True)
class HeartRateZones:
    """The five heart-rate zones returned for an activity."""

    activity_id: int
    zones: tuple[HeartRateZone, ...]

    def __post_init__(self) -> None:
        require_activity_id(self.activity_id)
        if len(self.zones) != 5:
            raise ValueError("An activity must contain exactly five heart-rate zones.")
        if tuple(zone.number for zone in self.zones) != (1, 2, 3, 4, 5):
            raise ValueError("Heart-rate zones must be ordered from one to five.")
