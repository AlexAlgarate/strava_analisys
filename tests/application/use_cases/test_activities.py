from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock, call

import pytest

from src.application.errors import ActivitiesNotFoundError
from src.application.ports.activity_gateway import ActivityGateway
from src.application.use_cases.activities import ActivityService
from src.domain.week_period import WeekPeriod
from tests.factories import activity_model

NOW = datetime(2026, 9, 9, 15, 30, tzinfo=UTC)


@pytest.fixture
def gateway() -> Mock:
    result = Mock(spec=ActivityGateway)
    result.list_activities = AsyncMock()
    result.get_activity_details = AsyncMock()
    return result


@pytest.fixture
def service(gateway: Mock) -> ActivityService:
    return ActivityService(gateway, clock=lambda: NOW)


@pytest.mark.asyncio
@pytest.mark.parametrize("previous_week", [False, True])
async def test_gets_activities_for_selected_week(
    service: ActivityService,
    gateway: Mock,
    previous_week: bool,
) -> None:
    activities = [activity_model()]
    gateway.list_activities.return_value = activities

    result = await service.get_activity_range(previous_week=previous_week)

    assert result == activities
    gateway.list_activities.assert_awaited_once_with(
        WeekPeriod.containing(NOW, previous_week=previous_week)
    )


@pytest.mark.asyncio
async def test_gets_details_for_every_weekly_activity(
    service: ActivityService,
    gateway: Mock,
) -> None:
    gateway.list_activities.return_value = [activity_model(1), activity_model(2)]
    details = [activity_model(1, "First"), activity_model(2, "Second")]
    gateway.get_activity_details.side_effect = details

    result = await service.get_activity_details()

    assert result == details
    assert gateway.get_activity_details.await_args_list == [call(1), call(2)]


@pytest.mark.asyncio
async def test_details_require_at_least_one_activity(
    service: ActivityService,
    gateway: Mock,
) -> None:
    gateway.list_activities.return_value = []

    with pytest.raises(ActivitiesNotFoundError, match="No activities found"):
        await service.get_activity_details()


@pytest.mark.asyncio
async def test_details_validate_concurrency_limit(gateway: Mock) -> None:
    gateway.list_activities.return_value = [activity_model()]
    service = ActivityService(gateway, clock=lambda: NOW, max_concurrency=0)

    with pytest.raises(ValueError, match="at least one"):
        await service.get_activity_details()
