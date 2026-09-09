from src.core.activities.fetchers import (
    ActivityData,
    DetailedActivitiesFetcher,
    WeeklyActivitiesFetcher,
)
from src.core.ports.export import ActivityDetailsWriter
from src.core.ports.strava import StravaAPI
from src.utils import constants as constant


class ActivityService:
    def __init__(
        self,
        api: StravaAPI,
        details_writer: ActivityDetailsWriter | None = None,
    ) -> None:
        self._api = api
        self._details_writer = details_writer

    async def get_activity_range(
        self, previous_week: bool = False
    ) -> list[ActivityData]:
        """Get activities within a specific date range."""
        return await WeeklyActivitiesFetcher(self._api).fetch_activity_data(
            previous_week=previous_week
        )

    async def get_activity_details(
        self, previous_week: bool = False
    ) -> list[ActivityData]:
        """Get detailed information for activities."""
        keys = [key.value for key in constant.ActivityDetailKey]
        return await DetailedActivitiesFetcher(
            self._api,
            writer=self._details_writer,
        ).fetch_activity_data(
            keys=keys,
            previous_week=previous_week,
        )
