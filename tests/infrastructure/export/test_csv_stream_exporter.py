import csv
from pathlib import Path

from src.infrastructure.export.csv_stream_exporter import CsvStreamExporter
from tests.factories import activity_stream


def test_writes_stream_samples_and_creates_parent_directory(tmp_path: Path) -> None:
    path = tmp_path / "nested" / "streams.csv"

    CsvStreamExporter().export((activity_stream(),), path)

    with path.open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    assert len(rows) == 3
    assert rows[0] == {
        "time": "0",
        "distance": "0.0",
        "heartrate": "120",
        "id": "1",
    }
