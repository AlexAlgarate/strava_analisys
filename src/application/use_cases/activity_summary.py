from src.application.ports.use_cases import ActivityQueries
from src.domain.activity_summary import WeeklyActivitySummary


class ActivitySummaryService:
    """Build a weekly summary from live detailed activity data."""

    def __init__(self, activities: ActivityQueries) -> None:
        self._activities = activities

    async def generate_summary(
        self,
        previous_week: bool = False,
    ) -> WeeklyActivitySummary:
        activities = await self._activities.get_activity_details(
            previous_week=previous_week
        )
        return WeeklyActivitySummary.from_activities(activities)
