from dataclasses import dataclass
from pathlib import Path

from src.domain.activity_stream import StreamBatch


@dataclass(frozen=True, slots=True)
class StreamExportResult:
    """Outcome of exporting a batch of activity streams."""

    batch: StreamBatch
    path: Path
