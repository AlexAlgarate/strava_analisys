from unittest.mock import AsyncMock, Mock

import pandas as pd
import pytest

from src.activities.detailed_activities import (
    DetailedActivitiesFetcher,
    WeeklyActivitiesFetcher,
)
from src.core.streams.fetcher import ActivityStreamsFetcher
from src.utils import constants as constant
from src.utils import exceptions


def _create_base_api_mock():
    api = Mock()
    api.get_headers = Mock(return_value={"Authorization": "Bearer test"})
    api.get_url = Mock(return_value="https://test.api.com/v3")
    return api


@pytest.fixture
def mock_async_api():
    api = _create_base_api_mock()
    api.make_request = AsyncMock()
    return api


@pytest.fixture
def mock_sync_api():
    api = _create_base_api_mock()
    api.make_request = Mock()
    return api


class TestWeeklyActivitiesFetcher:
    @pytest.fixture
    def activity_fetcher(self, mock_async_api):
        return WeeklyActivitiesFetcher(api=mock_async_api)

    @pytest.mark.asyncio
    async def test_fetch_activity_data_success(self, activity_fetcher, mock_async_api):
        expected_response = [{"id": 1}, {"id": 2}]
        mock_async_api.make_request.return_value = expected_response

        result = await activity_fetcher.fetch_activity_data()

        assert result == expected_response
        assert mock_async_api.make_request.call_count == 1
        call_args = mock_async_api.make_request.call_args[1]
        assert call_args["endpoint"] == "/activities"
        assert call_args["params"]["per_page"] == 200
        assert call_args["params"]["page"] == 1

    @pytest.mark.asyncio
    async def test_fetch_activity_data_previous_week(
        self, activity_fetcher, mock_async_api
    ):
        expected_response = [{"id": 3}, {"id": 4}]
        mock_async_api.make_request.return_value = expected_response

        result = await activity_fetcher.fetch_activity_data(previous_week=True)

        assert result == expected_response
        assert mock_async_api.make_request.call_count == 1


class TestDetailedActivitiesFetcher:
    @pytest.fixture
    def activity_fetcher(self, mock_async_api):
        return DetailedActivitiesFetcher(api=mock_async_api)

    @pytest.mark.asyncio
    async def test_fetch_activity_data_success(self, activity_fetcher, mock_async_api):
        mock_async_api.make_request.side_effect = [
            [{"id": 1}, {"id": 2}],
            {"id": 1, "name": "Activity 1"},
            {"id": 2, "name": "Activity 2"},
        ]

        result = await activity_fetcher.fetch_activity_data(
            keys=["id", "name"], previuos_week=False
        )

        assert len(result) == 2
        assert all(isinstance(activity, dict) for activity in result)
        assert all(set(activity.keys()) == {"id", "name"} for activity in result)

    @pytest.mark.asyncio
    async def test_fetch_activity_data_no_activities(
        self, activity_fetcher, mock_async_api
    ):
        mock_async_api.make_request.return_value = []

        with pytest.raises(ValueError, match="No activities found."):
            await activity_fetcher.fetch_activity_data(
                keys=["id", "name"], previuos_week=False
            )

    @pytest.mark.asyncio
    async def test_fetch_activity_details_error_handling(
        self, activity_fetcher, mock_async_api
    ):
        mock_async_api.make_request.side_effect = [
            [{"id": 1}],  # Weekly activities
            Exception("API Error"),  # Error fetching details
        ]

        result = await activity_fetcher.fetch_activity_data(
            keys=["id", "name"], previuos_week=False
        )

        assert len(result) == 1
        assert result[0] == {}  # Empty dict returned for failed fetch


STREAM_RESPONSES = [
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
    @pytest.fixture
    def stream_fetcher(self, mock_async_api):
        return ActivityStreamsFetcher(api=mock_async_api, id_activity=123)

    @pytest.mark.parametrize("stream_response", STREAM_RESPONSES)
    @pytest.mark.asyncio
    async def test_fetch_activity_data_success(
        self, stream_fetcher, mock_async_api, stream_response
    ):
        mock_async_api.make_request.return_value = stream_response

        result = await stream_fetcher.fetch_activity_data(
            stream_keys=constant.ACTIVITY_STREAMS_KEYS
        )

        assert isinstance(result, pd.DataFrame)
        assert list(result.columns) == ["time", "distance", "heartrate", "id"]
        assert len(result) == 3
        assert all(result["id"] == 123)

    @pytest.mark.asyncio
    async def test_fetch_activity_data_no_id(self, mock_async_api):
        fetcher = ActivityStreamsFetcher(api=mock_async_api)
        with pytest.raises(
            ValueError, match="Activity ID is required for this operation"
        ):
            await fetcher.fetch_activity_data(
                stream_keys=constant.ACTIVITY_STREAMS_KEYS
            )

    @pytest.mark.parametrize("stream_response", STREAM_RESPONSES)
    @pytest.mark.asyncio
    async def test_fetch_multiple_activities_streams(
        self, mock_async_api, stream_response
    ):
        activity_ids = [1, 2]

        mock_async_api.make_request.return_value = stream_response

        result = await ActivityStreamsFetcher.fetch_multiple_activities_streams(
            api=mock_async_api,
            list_id_activities=activity_ids,
            stream_keys=constant.ACTIVITY_STREAMS_KEYS,
        )

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 6  # 2 data points for each activity
        assert set(result["id"].unique()) == {1, 2}

    @pytest.mark.parametrize("stream_response", STREAM_RESPONSES)
    @pytest.mark.asyncio
    async def test_fetch_multiple_activities_streams_error_handling(
        self, mock_async_api, stream_response
    ):
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
