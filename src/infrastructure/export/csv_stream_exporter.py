import csv
from collections.abc import Sequence
from pathlib import Path

from src.domain.activity_stream import ActivityStream


class CsvStreamExporter:
    """Write activity stream data as CSV."""

    def export(self, streams: Sequence[ActivityStream], path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as output:
            writer = csv.DictWriter(
                output,
                fieldnames=("time", "distance", "heartrate", "id"),
            )
            writer.writeheader()
            writer.writerows(
                {
                    "time": sample.elapsed_seconds,
                    "distance": sample.distance_metres,
                    "heartrate": sample.heart_rate_bpm,
                    "id": stream.activity_id,
                }
                for stream in streams
                for sample in stream.samples
            )
