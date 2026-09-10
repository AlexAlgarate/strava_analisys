from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock, call

import pytest

from src.application.ports.activity_gateway import ActivityQueryGateway
from src.application.use_cases.activities import ActivityService
from src.domain.week_period import WeekPeriod, WeekSelection
from tests.factories import activity_model

NOW = datetime(2026, 9, 9, 15, 30, tzinfo=UTC)


@pytest.fixture
def gateway() -> Mock:
    result = Mock(spec=ActivityQueryGateway)
    result.list_activities = AsyncMock()
    result.get_activity_details = AsyncMock()
    return result


@pytest.fixture
def service(gateway: Mock) -> ActivityService:
    return ActivityService(gateway, clock=lambda: NOW)


@pytest.mark.asyncio
@pytest.mark.parametrize("week", list(WeekSelection))
async def test_lists_activities_for_selected_week(
    service: ActivityService,
    gateway: Mock,
    week: WeekSelection,
) -> None:
    activities = [activity_model()]
    gateway.list_activities.return_value = activities

    result = await service.list_activities(week=week)

    assert result == activities
    gateway.list_activities.assert_awaited_once_with(
        WeekPeriod.containing(NOW, week=week)
    )


@pytest.mark.asyncio
async def test_lists_details_for_every_weekly_activity(
    service: ActivityService,
    gateway: Mock,
) -> None:
    gateway.list_activities.return_value = [activity_model(1), activity_model(2)]
    details = [activity_model(1, "First"), activity_model(2, "Second")]
    gateway.get_activity_details.side_effect = details

    result = await service.list_detailed_activities(week=WeekSelection.CURRENT)

    assert result == details
    assert gateway.get_activity_details.await_args_list == [call(1), call(2)]


@pytest.mark.asyncio
async def test_details_return_an_empty_collection_when_the_week_has_no_activities(
    service: ActivityService,
    gateway: Mock,
) -> None:
    gateway.list_activities.return_value = []

    assert await service.list_detailed_activities(week=WeekSelection.CURRENT) == []
    gateway.get_activity_details.assert_not_awaited()


def test_service_rejects_invalid_concurrency_limit(gateway: Mock) -> None:
    with pytest.raises(ValueError, match="at least one"):
        ActivityService(gateway, clock=lambda: NOW, max_concurrency=0)

    gateway.list_activities.assert_not_awaited()
