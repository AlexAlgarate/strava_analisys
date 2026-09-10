import csv
from collections.abc import Sequence
from pathlib import Path

from src.domain.activity_stream import ActivityStream
from src.infrastructure.export.atomic_text_file import atomic_text_file


class CsvStreamExporter:
    """Write activity stream data as CSV."""

    def export(self, streams: Sequence[ActivityStream], path: Path) -> None:
        with atomic_text_file(path, newline="") as output:
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
