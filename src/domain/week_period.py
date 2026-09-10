from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Self


@dataclass(frozen=True, slots=True)
class WeekPeriod:
    """Half-open UTC interval covering one Monday-to-Monday week."""

    start: datetime
    end: datetime

    def __post_init__(self) -> None:
        for name, value in (("start", self.start), ("end", self.end)):
            if not isinstance(value, datetime):
                raise TypeError(f"Week {name} must be a datetime.")
            if value.tzinfo is None or value.utcoffset() is None:
                raise ValueError(f"Week {name} must be timezone-aware.")
        if self.end <= self.start:
            raise ValueError("Week end must be later than its start.")

    @classmethod
    def containing(
        cls,
        instant: datetime,
        *,
        previous_week: bool = False,
    ) -> Self:
        """Return the UTC week containing ``instant`` or the week before it."""
        if not isinstance(instant, datetime):
            raise TypeError("Week reference instant must be a datetime.")
        if instant.tzinfo is None or instant.utcoffset() is None:
            raise ValueError("Week reference instant must be timezone-aware.")

        utc_instant = instant.astimezone(UTC)
        start = utc_instant - timedelta(days=utc_instant.weekday())
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)
        if previous_week:
            start -= timedelta(weeks=1)
        return cls(start=start, end=start + timedelta(weeks=1))

    @property
    def start_epoch(self) -> int:
        return int(self.start.timestamp())

    @property
    def end_epoch(self) -> int:
        return int(self.end.timestamp())
