from typing import Protocol

from src.domain.activity_summary import WeeklyActivitySummary
from src.domain.detailed_activity import DetailedActivity


class DetailedActivityProvider(Protocol):
    async def get_activity_details(
        self, previous_week: bool = False
    ) -> list[DetailedActivity]: ...


class ActivitySummaryService:
    """Build a weekly summary from live detailed activity data."""

    def __init__(self, activity_provider: DetailedActivityProvider) -> None:
        self._activity_provider = activity_provider

    async def generate_summary(
        self, previous_week: bool = False
    ) -> WeeklyActivitySummary:
        activities = await self._activity_provider.get_activity_details(previous_week)
        return WeeklyActivitySummary.from_activities(activities)
