from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest

from src.application.ports.export import StreamExporter
from src.application.ports.use_cases import ActivityStreamQueries
from src.application.use_cases.stream_export import StreamExportService
from src.domain.activity_stream import StreamBatch
from tests.factories import activity_stream


@pytest.fixture
def streams() -> Mock:
    result = Mock(spec=ActivityStreamQueries)
    result.get_weekly_streams = AsyncMock()
    return result


@pytest.fixture
def exporter() -> Mock:
    return Mock(spec=StreamExporter)


@pytest.fixture
def service(streams: Mock, exporter: Mock) -> StreamExportService:
    return StreamExportService(streams, {"csv": exporter})


def test_exposes_normalized_supported_formats(
    streams: Mock,
    exporter: Mock,
) -> None:
    service = StreamExportService(streams, {"CSV": exporter})

    assert service.supported_formats == ("csv",)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("previous_week", "filename"),
    [
        (False, "streams_current_week.csv"),
        (True, "streams_previous_week.csv"),
    ],
)
async def test_exports_selected_week(
    service: StreamExportService,
    streams: Mock,
    exporter: Mock,
    tmp_path: Path,
    previous_week: bool,
    filename: str,
) -> None:
    batch = StreamBatch(streams=(activity_stream(),))
    streams.get_weekly_streams.return_value = batch

    result = await service.export_streams_for_selected_week(
        selected_format="CSV",
        output_dir=tmp_path,
        previous_week=previous_week,
    )

    assert result.batch is batch
    assert result.path == tmp_path / filename
    streams.get_weekly_streams.assert_awaited_once_with(
        previous_week=previous_week
    )
    exporter.export.assert_called_once_with(batch.streams, result.path)


@pytest.mark.asyncio
async def test_rejects_unsupported_format_before_loading_streams(
    service: StreamExportService,
    streams: Mock,
) -> None:
    with pytest.raises(ValueError, match="Unsupported format: json"):
        await service.export_streams_for_selected_week(selected_format="json")

    streams.get_weekly_streams.assert_not_awaited()
