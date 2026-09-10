from collections.abc import Sequence
from pathlib import Path
from typing import Protocol

from src.domain.activity_stream import ActivityStream
from src.domain.heart_rate_zones import HeartRateZones


class StreamExporter(Protocol):
    """Persist activity stream data in one output format."""

    def export(self, streams: Sequence[ActivityStream], path: Path, /) -> None: ...


class ActivityZonesWriter(Protocol):
    """Persist the zones associated with an activity."""

    def write(self, zones: HeartRateZones, /) -> Path: ...
