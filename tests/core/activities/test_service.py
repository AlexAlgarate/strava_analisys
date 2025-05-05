from unittest.mock import AsyncMock, Mock

import pytest

from src.core.activities.service import ActivityService


@pytest.fixture
def mock_async_api():
    api = Mock()
    api.make_request = AsyncMock()
    return api


@pytest.fixture
def activity_service(mock_async_api):
    return ActivityService(mock_async_api)


class TestActivityService:
    @pytest.mark.asyncio
    async def test_get_activity_range(self, activity_service, mock_async_api):
        mock_response = [{"id": 1}, {"id": 2}]
        mock_async_api.make_request.return_value = mock_response

        result = await activity_service.get_activity_range(previous_week=False)

        assert result == mock_response
        assert mock_async_api.make_request.called
        # Verify parameters of the call
        call_args = mock_async_api.make_request.call_args
        assert call_args.kwargs["endpoint"] == "/activities"
        assert "per_page" in call_args.kwargs["params"]
        assert "page" in call_args.kwargs["params"]

    @pytest.mark.asyncio
    async def test_get_activity_details(self, activity_service, mock_async_api):
        mock_activities = [{"id": 1}, {"id": 2}]
        mock_details = [
            {"id": 1, "name": "Activity 1"},
            {"id": 2, "name": "Activity 2"},
        ]
        mock_async_api.make_request.side_effect = [
            mock_activities,  # Weekly activities
            mock_details[0],  # Detailed activity 1
            mock_details[1],  # Detailed activity 2
        ]

        result = await activity_service.get_activity_details(previous_week=False)

        assert len(result) == 2
        assert all(isinstance(activity, dict) for activity in result)
        assert mock_async_api.make_request.call_count == 3
