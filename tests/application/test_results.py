from pathlib import Path

from src.application.results import ActivityZonesExportResult, StreamExportResult
from src.domain.activity_stream import StreamBatch
from tests.factories import heart_rate_zones


def test_stream_export_result_keeps_batch_and_path() -> None:
    batch = StreamBatch()

    result = StreamExportResult(batch=batch, path=Path("streams.csv"))

    assert result.batch is batch
    assert result.path == Path("streams.csv")


def test_activity_zones_export_result_keeps_zones_and_path() -> None:
    zones = heart_rate_zones(123)

    result = ActivityZonesExportResult(
        zones=zones,
        path=Path("zones_123.json"),
    )

    assert result.zones is zones
    assert result.path == Path("zones_123.json")
