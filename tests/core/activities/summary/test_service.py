from unittest.mock import AsyncMock, Mock

import pytest

from src.core.activities.summary.service import ActivitySummaryService
from src.domain.activity_summary import WeeklyActivitySummary
from src.domain.detailed_activity import DetailedActivity
from tests.factories import activity_payload


@pytest.mark.asyncio
async def test_generates_summary_from_live_activity_provider() -> None:
    activities = [DetailedActivity.from_mapping(activity_payload())]
    provider = Mock()
    provider.get_activity_details = AsyncMock(return_value=activities)
    service = ActivitySummaryService(provider)

    summary = await service.generate_summary(previous_week=True)

    assert isinstance(summary, WeeklyActivitySummary)
    assert summary.activity_count == 1
    provider.get_activity_details.assert_awaited_once_with(True)
