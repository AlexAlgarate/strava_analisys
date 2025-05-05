from unittest.mock import AsyncMock, Mock

import pandas as pd
import pytest

from src.strava_service import StravaService


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


@pytest.fixture
def service(mock_sync_api, mock_async_api):
    return StravaService(api_async=mock_async_api)


class TestStravaService:
    @pytest.mark.asyncio
    async def test_get_streams_for_activity(self, service, mock_async_api):
        mock_response = {
            "time": {"data": [0, 1]},
            "distance": {"data": [0, 100]},
            "heartrate": {"data": [60, 65]},
        }
        mock_async_api.make_request.return_value = mock_response

        result = await service.get_streams_for_activity(activity_id=123)

        assert isinstance(result, pd.DataFrame)
        assert list(result.columns) == ["time", "distance", "heartrate", "id"]
        assert len(result) == 2
        assert all(result["id"] == 123)

    @pytest.mark.asyncio
    async def test_get_streams_for_multiple_activities(self, service, mock_async_api):
        mock_response = {
            "time": {"data": [0, 1]},
            "distance": {"data": [0, 100]},
            "heartrate": {"data": [60, 65]},
        }
        mock_async_api.make_request.return_value = mock_response

        result = await service.get_streams_for_multiple_activities(activity_ids=[1, 2])

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 4  # 2 data points for each activity
        assert set(result["id"].unique()) == {1, 2}

    @pytest.mark.asyncio
    async def test_export_streams_for_selected_week(
        self, service, mock_async_api, tmp_path
    ):
        # Mock responses for activities and streams
        mock_activities = [{"id": 1}, {"id": 2}]
        mock_stream_data = {
            "time": {"data": [0, 1]},
            "distance": {"data": [0, 100]},
            "heartrate": {"data": [60, 65]},
        }
        mock_async_api.make_request.side_effect = [
            mock_activities,
            mock_stream_data,
            mock_stream_data,
        ]

        result = await service.export_streams_for_selected_week(
            output_dir=str(tmp_path), previous_week=True
        )

        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        assert (tmp_path / "streams_previous_week.csv").exists()

    @pytest.mark.asyncio
    async def test_get_activity_range(self, service, mock_async_api):
        mock_response = [{"id": 1}, {"id": 2}]
        mock_async_api.make_request.return_value = mock_response

        result = await service.get_activity_range(previous_week=False)

        assert result == mock_response
        assert mock_async_api.make_request.called

    @pytest.mark.asyncio
    async def test_get_activity_details(self, service, mock_async_api):
        # Mock responses for both weekly activities and detailed activities
        mock_async_api.make_request.side_effect = [
            [{"id": 1}, {"id": 2}],  # Weekly activities
            {"id": 1, "name": "Activity 1"},  # Detailed activity 1
            {"id": 2, "name": "Activity 2"},  # Detailed activity 2
        ]

        result = await service.get_activity_details(previous_week=False)

        assert len(result) == 2
        assert all(isinstance(activity, dict) for activity in result)
        assert mock_async_api.make_request.call_count == 3

    @pytest.mark.asyncio
    async def test_get_activity_zones(self, service, mock_async_api):
        mock_response = {"distribution_buckets": [10, 20, 30, 40, 50]}
        mock_async_api.make_request.return_value = mock_response

        result = await service.get_activity_zones(activity_id=123)

        assert isinstance(result, dict)
        assert len(result) == 5
        assert all(f"Zone_{i}" in result for i in range(1, 6))
        assert list(result.values()) == [10, 20, 30, 40, 50]

    @pytest.mark.asyncio
    async def test_get_activity_zones_no_heartrate(self, service, mock_async_api):
        mock_response = {"distribution_buckets": None}
        mock_async_api.make_request.return_value = mock_response

        with pytest.raises(ValueError, match="does not have heartrate information"):
            await service.get_activity_zones(activity_id=123)
