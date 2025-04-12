from unittest.mock import AsyncMock, Mock

import pandas as pd
import pytest

from src.strava_service import StravaService


@pytest.fixture
def sync_api():
    api = Mock()
    api.make_request = Mock()
    return api


@pytest.fixture
def async_api():
    api = Mock()
    api.make_request_async = AsyncMock()
    return api


@pytest.fixture
def service(sync_api, async_api):
    return StravaService(api_sync=sync_api, api_async=async_api)


class TestStravaService:
    @pytest.mark.asyncio
    async def test_get_streams_for_activity(self, service, async_api):
        mock_response = {
            "time": {"data": [0, 1]},
            "distance": {"data": [0, 100]},
            "heartrate": {"data": [60, 65]},
        }
        async_api.make_request_async.return_value = mock_response

        result = await service.get_streams_for_activity(activity_id=123)

        assert isinstance(result, pd.DataFrame)
        assert list(result.columns) == ["time", "distance", "heartrate", "id"]
        assert len(result) == 2
        assert all(result["id"] == 123)

    @pytest.mark.asyncio
    async def test_get_streams_for_multiple_activities(self, service, async_api):
        mock_response = {
            "time": {"data": [0, 1]},
            "distance": {"data": [0, 100]},
            "heartrate": {"data": [60, 65]},
        }
        async_api.make_request_async.return_value = mock_response

        result = await service.get_streams_for_multiple_activities(activity_ids=[1, 2])

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 4  # 2 data points for each activity
        assert set(result["id"].unique()) == {1, 2}

    @pytest.mark.asyncio
    async def test_get_activity_range(self, service, async_api):
        mock_response = [{"id": 1}, {"id": 2}]
        async_api.make_request_async.return_value = mock_response

        result = await service.get_activity_range(previous_week=False)

        assert result == mock_response
        assert async_api.make_request_async.called

    @pytest.mark.asyncio
    async def test_get_activity_details(self, service, async_api):
        # Mock responses for both weekly activities and detailed activities
        async_api.make_request_async.side_effect = [
            [{"id": 1}, {"id": 2}],  # Weekly activities
            {"id": 1, "name": "Activity 1"},  # Detailed activity 1
            {"id": 2, "name": "Activity 2"},  # Detailed activity 2
        ]

        result = await service.get_activity_details(previous_week=False)

        assert len(result) == 2
        assert all(isinstance(activity, dict) for activity in result)
        assert async_api.make_request_async.call_count == 3

    def test_get_one_activity(self, service, sync_api):
        expected_response = {"id": 123, "name": "Morning Run"}
        sync_api.make_request.return_value = expected_response

        result = service.get_one_activity(activity_id=123)

        assert result == expected_response
        sync_api.make_request.assert_called_once_with("/activities/123")

    def test_get_last_200_activities(self, service, sync_api):
        expected_response = [{"id": 1}, {"id": 2}]
        sync_api.make_request.return_value = expected_response

        result = service.get_last_200_activities()

        assert result == expected_response
        sync_api.make_request.assert_called_once_with(
            endpoint="/activities", params={"per_page": 200, "page": 1}
        )
