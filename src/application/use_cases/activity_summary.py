from src.application.ports.use_cases import ActivityQueries
from src.domain.activity_summary import WeeklyActivitySummary
from src.domain.week_period import WeekSelection


class ActivitySummaryService:
    """Build a weekly summary from live detailed activity data."""

    def __init__(self, activities: ActivityQueries) -> None:
        self._activities = activities

    async def generate_summary(
        self,
        *,
        week: WeekSelection,
    ) -> WeeklyActivitySummary:
        activities = await self._activities.get_activity_details(week=week)
        return WeeklyActivitySummary.from_activities(activities)
