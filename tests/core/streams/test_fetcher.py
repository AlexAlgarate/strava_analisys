from typing import Dict, List
from unittest.mock import AsyncMock, Mock

import pandas as pd
import pytest

from src.core.streams.fetcher import ActivityStreamsFetcher
from src.utils import constants as constant
from src.utils import exceptions


@pytest.fixture
def mock_async_api() -> Mock:
    api = Mock()
    api.make_request = AsyncMock()
    return api


@pytest.fixture
def stream_fetcher(mock_async_api: Mock) -> ActivityStreamsFetcher:
    return ActivityStreamsFetcher(api=mock_async_api, id_activity=123)


stream_response_type = List[Dict[str, Dict[str, List[float]]]]
STREAM_RESPONSES: stream_response_type = [
    {
        "time": {"data": [0, 1, 2]},
        "distance": {"data": [0, 1, 2]},
        "heartrate": {"data": [60, 62, 64]},
    },
    {
        "time": {"data": [3, 4, 5]},
        "distance": {"data": [0, 10, 20]},
        "heartrate": {"data": [100, 101, 102]},
    },
    {
        "time": {"data": [6, 7, 8]},
        "distance": {"data": [0.5, 20.5, 40.5]},
        "heartrate": {"data": [110, 111, 112]},
    },
]


class TestActivityStreamsFetcher:
    @pytest.mark.parametrize("stream_response", STREAM_RESPONSES)
    @pytest.mark.asyncio
    async def test_fetch_activity_data_success(
        self,
        stream_fetcher: ActivityStreamsFetcher,
        mock_async_api: Mock,
        stream_response: stream_response_type,
    ) -> None:
        mock_async_api.make_request.return_value = stream_response

        result = await stream_fetcher.fetch_activity_data(
            stream_keys=constant.ACTIVITY_STREAMS_KEYS
        )

        assert isinstance(result, pd.DataFrame)
        assert list(result.columns) == ["time", "distance", "heartrate", "id"]
        assert len(result) == 3
        assert all(result["id"] == 123)

    @pytest.mark.asyncio
    async def test_fetch_activity_data_no_id(self, mock_async_api: Mock) -> None:
        fetcher = ActivityStreamsFetcher(api=mock_async_api)
        with pytest.raises(ValueError, match="Activity ID is required"):
            await fetcher.fetch_activity_data(
                stream_keys=constant.ACTIVITY_STREAMS_KEYS
            )

    @pytest.mark.parametrize("stream_response", STREAM_RESPONSES)
    @pytest.mark.asyncio
    async def test_fetch_multiple_activities_streams(
        self,
        mock_async_api: Mock,
        stream_response: stream_response_type,
    ) -> None:
        activity_ids = [1, 2]
        mock_async_api.make_request.return_value = stream_response

        result = await ActivityStreamsFetcher.fetch_multiple_activities_streams(
            api=mock_async_api,
            list_id_activities=activity_ids,
            stream_keys=constant.ACTIVITY_STREAMS_KEYS,
        )

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 6  # 2 activities × 3 data points each
        assert set(result["id"].unique()) == {1, 2}

    @pytest.mark.parametrize("stream_response", STREAM_RESPONSES)
    @pytest.mark.asyncio
    async def test_fetch_multiple_activities_streams_error_handling(
        self,
        mock_async_api: Mock,
        stream_response: stream_response_type,
    ) -> None:
        activity_ids = [1, 2]
        mock_async_api.make_request.side_effect = [
            stream_response,
            exceptions.TooManyRequestError("Rate limit exceeded"),
        ]

        result = await ActivityStreamsFetcher.fetch_multiple_activities_streams(
            api=mock_async_api,
            list_id_activities=activity_ids,
            stream_keys=constant.ACTIVITY_STREAMS_KEYS,
        )

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3  # Only data from successful request
