from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock

import pytest

from src.application.ports.activity_gateway import ActivityGateway
from src.application.ports.use_cases import ActivityQueries
from src.application.use_cases.activities import ActivityService
from src.application.use_cases.activity_summary import ActivitySummaryService
from src.domain.activity_summary import WeeklyActivitySummary
from src.domain.week_period import WeekSelection
from tests.factories import activity_model


@pytest.mark.asyncio
async def test_generates_summary_from_detailed_activities() -> None:
    activities = [activity_model()]
    activity_queries = Mock(spec=ActivityQueries)
    activity_queries.get_activity_details = AsyncMock(return_value=activities)
    service = ActivitySummaryService(activity_queries)

    summary = await service.generate_summary(week=WeekSelection.PREVIOUS)

    assert isinstance(summary, WeeklyActivitySummary)
    assert summary.activity_count == 1
    activity_queries.get_activity_details.assert_awaited_once_with(
        week=WeekSelection.PREVIOUS
    )


@pytest.mark.asyncio
async def test_empty_week_produces_an_empty_summary_across_real_use_cases() -> None:
    gateway = Mock(spec=ActivityGateway)
    gateway.list_activities = AsyncMock(return_value=[])
    gateway.get_activity_details = AsyncMock()
    activities = ActivityService(
        gateway,
        clock=lambda: datetime(2026, 9, 9, tzinfo=UTC),
    )

    summary = await ActivitySummaryService(activities).generate_summary(
        week=WeekSelection.CURRENT
    )

    assert summary == WeeklyActivitySummary.from_activities([])
    gateway.get_activity_details.assert_not_awaited()
