from unittest.mock import AsyncMock, Mock

import pytest

from src.application.ports.use_cases import ActivityQueries
from src.application.use_cases.activity_summary import ActivitySummaryService
from src.domain.activity_summary import WeeklyActivitySummary
from tests.factories import activity_model


@pytest.mark.asyncio
async def test_generates_summary_from_detailed_activities() -> None:
    activities = [activity_model()]
    activity_queries = Mock(spec=ActivityQueries)
    activity_queries.get_activity_details = AsyncMock(return_value=activities)
    service = ActivitySummaryService(activity_queries)

    summary = await service.generate_summary(previous_week=True)

    assert isinstance(summary, WeeklyActivitySummary)
    assert summary.activity_count == 1
    activity_queries.get_activity_details.assert_awaited_once_with(
        previous_week=True
    )
