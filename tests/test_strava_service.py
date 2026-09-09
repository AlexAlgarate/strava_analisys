from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest

from src.core.service import StravaService
from src.domain.activity_stream import ActivityStream, StreamBatch
from src.domain.detailed_activity import DetailedActivity
from src.domain.heart_rate_zones import HeartRateZones
from src.infrastructure.export.csv_stream_exporter import CsvStreamExporter
from tests.factories import activity_payload, stream_payload, zones_payload


@pytest.fixture
def mock_async_api() -> Mock:
    api = Mock()
    api.make_request = AsyncMock()
    return api


@pytest.fixture
def service(mock_async_api: Mock) -> StravaService:
    return StravaService(
        api=mock_async_api,
        exporters={"csv": CsvStreamExporter()},
    )


@pytest.mark.asyncio
async def test_get_streams_for_activity(
    service: StravaService,
    mock_async_api: Mock,
) -> None:
    mock_async_api.make_request.return_value = stream_payload()

    result = await service.get_streams_for_activity(activity_id=123)

    assert isinstance(result, ActivityStream)
    assert result.activity_id == 123


@pytest.mark.asyncio
async def test_get_streams_for_multiple_activities(
    service: StravaService,
    mock_async_api: Mock,
) -> None:
    mock_async_api.make_request.return_value = stream_payload()

    result = await service.get_streams_for_multiple_activities(activity_ids=[1, 2])

    assert isinstance(result, StreamBatch)
    assert result.sample_count == 6


@pytest.mark.asyncio
async def test_export_streams_for_selected_week(
    service: StravaService,
    mock_async_api: Mock,
    tmp_path: Path,
) -> None:
    mock_async_api.make_request.side_effect = [
        [activity_payload(1), activity_payload(2)],
        stream_payload(),
        stream_payload(),
    ]

    result = await service.export_streams_for_selected_week(
        output_dir=tmp_path,
        previous_week=True,
    )

    assert isinstance(result, StreamBatch)
    assert result.sample_count == 6
    assert (tmp_path / "streams_previous_week.csv").exists()


@pytest.mark.asyncio
async def test_get_activity_range(
    service: StravaService,
    mock_async_api: Mock,
) -> None:
    mock_async_api.make_request.return_value = [
        activity_payload(1),
        activity_payload(2),
    ]

    result = await service.get_activity_range(previous_week=False)

    assert [activity.id for activity in result] == [1, 2]


@pytest.mark.asyncio
async def test_get_activity_details(
    service: StravaService,
    mock_async_api: Mock,
) -> None:
    mock_async_api.make_request.side_effect = [
        [activity_payload(1), activity_payload(2)],
        activity_payload(1, "Activity 1"),
        activity_payload(2, "Activity 2"),
    ]

    result = await service.get_activity_details(previous_week=False)

    assert len(result) == 2
    assert all(isinstance(activity, DetailedActivity) for activity in result)


@pytest.mark.asyncio
async def test_get_activity_zones(
    service: StravaService,
    mock_async_api: Mock,
) -> None:
    mock_async_api.make_request.return_value = zones_payload()

    result = await service.get_activity_zones(activity_id=123)

    assert isinstance(result, HeartRateZones)
    assert len(result.zones) == 5


@pytest.mark.asyncio
async def test_get_activity_zones_without_heartrate(
    service: StravaService,
    mock_async_api: Mock,
) -> None:
    mock_async_api.make_request.return_value = {"distribution_buckets": None}

    with pytest.raises(ValueError, match="does not have heartrate information"):
        await service.get_activity_zones(activity_id=123)
