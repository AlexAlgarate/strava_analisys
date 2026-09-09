from unittest.mock import AsyncMock, Mock

import pytest

from src.core.streams.manager import StreamManager
from src.domain.activity_stream import ActivityStream, StreamBatch
from tests.factories import activity_payload, stream_payload


@pytest.fixture
def mock_async_api() -> Mock:
    api = Mock()
    api.make_request = AsyncMock()
    return api


@pytest.fixture
def stream_manager(mock_async_api: Mock) -> StreamManager:
    return StreamManager(mock_async_api)


@pytest.mark.asyncio
async def test_get_streams_for_activity(
    stream_manager: StreamManager,
    mock_async_api: Mock,
) -> None:
    mock_async_api.make_request.return_value = stream_payload(times=[0, 1])

    result = await stream_manager.get_streams_for_activity(activity_id=123)

    assert isinstance(result, ActivityStream)
    assert len(result.samples) == 3
    assert result.activity_id == 123


@pytest.mark.asyncio
async def test_get_streams_for_multiple_activities(
    stream_manager: StreamManager,
    mock_async_api: Mock,
) -> None:
    mock_async_api.make_request.return_value = stream_payload()

    result = await stream_manager.get_streams_for_multiple_activities(
        activity_ids=[1, 2]
    )

    assert isinstance(result, StreamBatch)
    assert result.sample_count == 6
    assert [stream.activity_id for stream in result.streams] == [1, 2]


@pytest.mark.asyncio
async def test_get_weekly_streams(
    stream_manager: StreamManager,
    mock_async_api: Mock,
) -> None:
    mock_async_api.make_request.side_effect = [
        [activity_payload(1), activity_payload(2)],
        stream_payload(),
        stream_payload(),
    ]

    result = await stream_manager.get_weekly_streams(previous_week=False)

    assert isinstance(result, StreamBatch)
    assert result.sample_count == 6
    assert [stream.activity_id for stream in result.streams] == [1, 2]
    assert mock_async_api.make_request.call_count == 3
