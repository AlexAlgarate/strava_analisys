from src.core.activities.fetchers import (
    DetailedActivitiesFetcher,
    WeeklyActivitiesFetcher,
)
from src.core.concurrency import DEFAULT_MAX_CONCURRENCY
from src.core.ports.strava import StravaAPI
from src.domain.detailed_activity import DetailedActivity


class ActivityService:
    def __init__(
        self,
        api: StravaAPI,
        *,
        max_concurrency: int = DEFAULT_MAX_CONCURRENCY,
    ) -> None:
        self._api = api
        self._max_concurrency = max_concurrency

    async def get_activity_range(
        self, previous_week: bool = False
    ) -> list[DetailedActivity]:
        """Get activities within a specific date range."""
        return await WeeklyActivitiesFetcher(self._api).fetch_activity_data(
            previous_week=previous_week
        )

    async def get_activity_details(
        self, previous_week: bool = False
    ) -> list[DetailedActivity]:
        """Get detailed information for activities."""
        return await DetailedActivitiesFetcher(
            self._api,
            max_concurrency=self._max_concurrency,
        ).fetch_activity_data(
            previous_week=previous_week,
        )
