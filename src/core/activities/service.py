from src.core.activities.fetchers import (
    ActivityData,
    DetailedActivitiesFetcher,
    WeeklyActivitiesFetcher,
)
from src.core.ports.strava import StravaAPI
from src.domain.detailed_activity import DetailedActivity


class ActivityService:
    def __init__(self, api: StravaAPI) -> None:
        self._api = api

    async def get_activity_range(
        self, previous_week: bool = False
    ) -> list[ActivityData]:
        """Get activities within a specific date range."""
        return await WeeklyActivitiesFetcher(self._api).fetch_activity_data(
            previous_week=previous_week
        )

    async def get_activity_details(
        self, previous_week: bool = False
    ) -> list[DetailedActivity]:
        """Get detailed information for activities."""
        return await DetailedActivitiesFetcher(self._api).fetch_activity_data(
            previous_week=previous_week,
        )
