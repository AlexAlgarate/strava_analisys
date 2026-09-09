from unittest.mock import AsyncMock, Mock

import pytest

import src.core.activities.fetchers as fetchers_module
from src.core.activities.fetchers import (
    DetailedActivitiesFetcher,
    WeeklyActivitiesFetcher,
)
from src.domain.detailed_activity import DetailedActivity
from tests.factories import activity_payload


def _create_base_api_mock() -> Mock:
    api = Mock()
    api.get_headers = Mock(return_value={"Authorization": "Bearer test"})
    api.get_url = Mock(return_value="https://test.api.com/v3")
    return api


@pytest.fixture
def mock_async_api() -> Mock:
    api = _create_base_api_mock()
    api.make_request = AsyncMock()
    return api


class TestWeeklyActivitiesFetcher:
    @pytest.fixture
    def activity_fetcher(self, mock_async_api: Mock) -> WeeklyActivitiesFetcher:
        return WeeklyActivitiesFetcher(api=mock_async_api)

    @pytest.mark.asyncio
    async def test_fetch_activity_data_success(
        self, activity_fetcher: WeeklyActivitiesFetcher, mock_async_api: Mock
    ) -> None:
        expected_response = [activity_payload(1), activity_payload(2)]
        mock_async_api.make_request.return_value = expected_response

        result = await activity_fetcher.fetch_activity_data()

        assert [activity.id for activity in result] == [1, 2]
        assert mock_async_api.make_request.call_count == 1
        call_args = mock_async_api.make_request.call_args[1]
        assert call_args["endpoint"] == "/activities"
        assert call_args["params"]["per_page"] == 200
        assert call_args["params"]["page"] == 1

    @pytest.mark.asyncio
    async def test_fetch_activity_data_previous_week(
        self, activity_fetcher: WeeklyActivitiesFetcher, mock_async_api: Mock
    ) -> None:
        expected_response = [activity_payload(3), activity_payload(4)]
        mock_async_api.make_request.return_value = expected_response

        result = await activity_fetcher.fetch_activity_data(previous_week=True)

        assert [activity.id for activity in result] == [3, 4]
        assert mock_async_api.make_request.call_count == 1

    @pytest.mark.asyncio
    async def test_fetches_all_activity_pages(
        self,
        activity_fetcher: WeeklyActivitiesFetcher,
        mock_async_api: Mock,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(fetchers_module, "ACTIVITIES_PAGE_SIZE", 2)
        mock_async_api.make_request.side_effect = [
            [activity_payload(1), activity_payload(2)],
            [activity_payload(3)],
        ]

        result = await activity_fetcher.fetch_activity_data()

        assert [activity.id for activity in result] == [1, 2, 3]
        assert (
            mock_async_api.make_request.await_args_list[1].kwargs["params"]["page"] == 2
        )

    @pytest.mark.asyncio
    async def test_rejects_non_list_response(
        self, activity_fetcher: WeeklyActivitiesFetcher, mock_async_api: Mock
    ) -> None:
        mock_async_api.make_request.return_value = {"id": 1}

        with pytest.raises(TypeError, match="response must be a list"):
            await activity_fetcher.fetch_activity_data()

    @pytest.mark.asyncio
    async def test_rejects_non_object_activity(
        self, activity_fetcher: WeeklyActivitiesFetcher, mock_async_api: Mock
    ) -> None:
        mock_async_api.make_request.return_value = ["invalid"]

        with pytest.raises(TypeError, match="activity must be an object"):
            await activity_fetcher.fetch_activity_data()


class TestDetailedActivitiesFetcher:
    @pytest.fixture
    def activity_fetcher(self, mock_async_api: Mock) -> DetailedActivitiesFetcher:
        return DetailedActivitiesFetcher(api=mock_async_api)

    @pytest.mark.asyncio
    async def test_fetch_activity_data_success(
        self, activity_fetcher: DetailedActivitiesFetcher, mock_async_api: Mock
    ) -> None:
        mock_async_api.make_request.side_effect = [
            [activity_payload(1), activity_payload(2)],
            activity_payload(1, "Activity 1"),
            activity_payload(2, "Activity 2"),
        ]

        result = await activity_fetcher.fetch_activity_data(previous_week=False)

        assert len(result) == 2
        assert all(isinstance(activity, DetailedActivity) for activity in result)
        assert [activity.name for activity in result] == ["Activity 1", "Activity 2"]

    @pytest.mark.asyncio
    async def test_fetch_activity_data_no_activities(
        self, activity_fetcher: DetailedActivitiesFetcher, mock_async_api: Mock
    ) -> None:
        mock_async_api.make_request.return_value = []

        with pytest.raises(ValueError, match="No activities found."):
            await activity_fetcher.fetch_activity_data(previous_week=False)

    @pytest.mark.asyncio
    async def test_fetch_activity_details_error_handling(
        self, activity_fetcher: DetailedActivitiesFetcher, mock_async_api: Mock
    ) -> None:
        mock_async_api.make_request.side_effect = [
            [activity_payload(1)],  # Weekly activities
            Exception("API Error"),  # Error fetching details
        ]

        with pytest.raises(Exception, match="API Error"):
            await activity_fetcher.fetch_activity_data(previous_week=False)

    @pytest.mark.asyncio
    async def test_rejects_activity_without_integer_id(
        self, activity_fetcher: DetailedActivitiesFetcher, mock_async_api: Mock
    ) -> None:
        mock_async_api.make_request.return_value = [activity_payload(id=True)]

        with pytest.raises(TypeError, match="id must be an integer"):
            await activity_fetcher.fetch_activity_data()
