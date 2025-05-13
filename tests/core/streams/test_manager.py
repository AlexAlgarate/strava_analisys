from unittest.mock import AsyncMock, Mock

import pandas as pd
import pytest

from src.core.streams.manager import StreamManager


@pytest.fixture
def mock_async_api() -> Mock:
    api = Mock()
    api.make_request = AsyncMock()
    return api


@pytest.fixture
def stream_manager(mock_async_api: Mock) -> StreamManager:
    return StreamManager(mock_async_api)


class TestStreamManager:
    @pytest.mark.asyncio
    async def test_get_streams_for_activity(
        self, stream_manager: StreamManager, mock_async_api: Mock
    ) -> None:
        mock_response = {
            "time": {"data": [0, 1]},
            "distance": {"data": [0, 100]},
            "heartrate": {"data": [60, 65]},
        }
        mock_async_api.make_request.return_value = mock_response

        result = await stream_manager.get_streams_for_activity(activity_id=123)

        assert isinstance(result, pd.DataFrame)
        assert list(result.columns) == ["time", "distance", "heartrate", "id"]
        assert len(result) == 2
        assert all(result["id"] == 123)
        assert mock_async_api.make_request.call_count == 1

    @pytest.mark.asyncio
    async def test_get_streams_for_multiple_activities(
        self, stream_manager: StreamManager, mock_async_api: Mock
    ) -> None:
        mock_response = {
            "time": {"data": [0, 1]},
            "distance": {"data": [0, 100]},
            "heartrate": {"data": [60, 65]},
        }
        mock_async_api.make_request.return_value = mock_response

        result = await stream_manager.get_streams_for_multiple_activities(
            activity_ids=[1, 2]
        )

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 4  # 2 data points for each activity
        assert set(result["id"].unique()) == {1, 2}
        assert mock_async_api.make_request.call_count == 2  # One call per activity

    @pytest.mark.asyncio
    async def test_get_weekly_streams(
        self, stream_manager: StreamManager, mock_async_api: Mock
    ) -> None:
        mock_activities = [{"id": 1}, {"id": 2}]
        mock_stream_data = {
            "time": {"data": [0, 1]},
            "distance": {"data": [0, 100]},
            "heartrate": {"data": [60, 65]},
        }

        # Configure mock to return different responses for each call
        mock_async_api.make_request.side_effect = [
            mock_activities,  # Response for weekly activities
            mock_stream_data,  # Stream data for activity 1
            mock_stream_data,  # Stream data for activity 2
        ]

        result = await stream_manager.get_weekly_streams(previous_week=False)

        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        assert set(result["id"].unique()) == {1, 2}
        assert len(result) == 4  # 2 activities × 2 data points each
        assert (
            mock_async_api.make_request.call_count == 3
        )  # Activities + 2 stream calls
