import csv
from collections.abc import Sequence
from pathlib import Path

import pytest

from src.core.streams.exporter import DataExporter
from src.domain.activity_stream import ActivityStream
from src.infrastructure.export.csv_stream_exporter import CsvStreamExporter
from tests.factories import stream_payload


class CountingExporter:
    def __init__(self) -> None:
        self.export_count = 0

    def export(self, streams: Sequence[ActivityStream], path: Path) -> None:
        self.export_count += 1


@pytest.fixture
def sample_streams() -> tuple[ActivityStream, ...]:
    return (ActivityStream.from_mapping(1, stream_payload()),)


@pytest.fixture
def data_exporter() -> DataExporter:
    return DataExporter({"csv": CsvStreamExporter()})


def test_csv_exporter_creates_parent_directory(
    sample_streams: tuple[ActivityStream, ...],
    tmp_path: Path,
) -> None:
    path = tmp_path / "nested" / "test.csv"

    CsvStreamExporter().export(sample_streams, path)

    with path.open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    assert len(rows) == 3
    assert rows[0] == {
        "time": "0",
        "distance": "0.0",
        "heartrate": "120",
        "id": "1",
    }


def test_exposes_immutable_supported_formats(data_exporter: DataExporter) -> None:
    assert data_exporter.supported_formats == ("csv",)


def test_create_path(data_exporter: DataExporter) -> None:
    assert data_exporter._create_path("test_dir", True, "csv") == Path(
        "test_dir/streams_previous_week.csv"
    )
    assert data_exporter._create_path("test_dir", False, "csv") == Path(
        "test_dir/streams_current_week.csv"
    )


def test_export_streams_rejects_invalid_format(
    data_exporter: DataExporter,
    sample_streams: tuple[ActivityStream, ...],
) -> None:
    with pytest.raises(ValueError, match="Unsupported format: invalid"):
        data_exporter.export_streams(sample_streams, selected_format="invalid")


def test_export_streams_returns_created_path(
    data_exporter: DataExporter,
    sample_streams: tuple[ActivityStream, ...],
    tmp_path: Path,
) -> None:
    path = data_exporter.export_streams(
        sample_streams,
        selected_format="CSV",
        output_dir=tmp_path,
        previous_week=True,
    )

    assert path == tmp_path / "streams_previous_week.csv"
    assert path.exists()


def test_export_streams_delegates_to_custom_exporter(
    sample_streams: tuple[ActivityStream, ...],
) -> None:
    counting_exporter = CountingExporter()
    exporter = DataExporter({"counter": counting_exporter})

    exporter.export_streams(sample_streams, selected_format="counter")

    assert counting_exporter.export_count == 1
