from pathlib import Path

from src.application.results import StreamExportResult
from src.domain.activity_stream import StreamBatch


def test_stream_export_result_keeps_batch_and_path() -> None:
    batch = StreamBatch()

    result = StreamExportResult(batch=batch, path=Path("streams.csv"))

    assert result.batch is batch
    assert result.path == Path("streams.csv")
