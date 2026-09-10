from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Self


class WeekSelection(Enum):
    """A week selected relative to a reference instant."""

    CURRENT = "current"
    PREVIOUS = "previous"


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
        if self.start.utcoffset() != timedelta(0) or self.end.utcoffset() != timedelta(
            0
        ):
            raise ValueError("Week boundaries must be in UTC.")
        if self.start.weekday() != 0 or self.start.time() != datetime.min.time():
            raise ValueError("A week must start on Monday at midnight UTC.")
        if self.end - self.start != timedelta(weeks=1):
            raise ValueError("A week must span exactly seven days.")

    @classmethod
    def containing(
        cls,
        instant: datetime,
        *,
        week: WeekSelection,
    ) -> Self:
        """Return the selected UTC week relative to ``instant``."""
        if not isinstance(instant, datetime):
            raise TypeError("Week reference instant must be a datetime.")
        if instant.tzinfo is None or instant.utcoffset() is None:
            raise ValueError("Week reference instant must be timezone-aware.")
        if not isinstance(week, WeekSelection):
            raise TypeError("Week selection must be a WeekSelection value.")

        utc_instant = instant.astimezone(UTC)
        start = utc_instant - timedelta(days=utc_instant.weekday())
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)
        if week is WeekSelection.PREVIOUS:
            start -= timedelta(weeks=1)
        return cls(start=start, end=start + timedelta(weeks=1))

    @property
    def start_epoch(self) -> int:
        return int(self.start.timestamp())

    @property
    def end_epoch(self) -> int:
        return int(self.end.timestamp())
