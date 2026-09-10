from dataclasses import dataclass
from pathlib import Path

from src.domain.activity_stream import StreamBatch
from src.domain.heart_rate_zones import HeartRateZones


@dataclass(frozen=True, slots=True)
class StreamExportResult:
    """Outcome of exporting a batch of activity streams."""

    batch: StreamBatch
    path: Path


@dataclass(frozen=True, slots=True)
class ActivityZonesExportResult:
    """Outcome of exporting the heart-rate zones for one activity."""

    zones: HeartRateZones
    path: Path
