from typing import Any, Dict, List

from src.activities.detailed_activities import (
    DetailedActivitiesFetcher,
    WeeklyActivitiesFetcher,
)
from src.infrastructure.api_clients.async_strava_api import AsyncStravaAPI
from src.utils import constants as constant


class ActivityService:
    def __init__(self, api_async: AsyncStravaAPI):
        self.api_async = api_async

    async def get_activity_range(self, previous_week: bool = False) -> Any:
        """Get activities within a specific date range."""
        return await WeeklyActivitiesFetcher(self.api_async).fetch_activity_data(
            previous_week=previous_week
        )

    async def get_activity_details(
        self, previous_week: bool = False
    ) -> List[Dict[Any, Any]]:
        """Get detailed information for activities."""
        keys = [key.value for key in constant.ActivityDetailKey]
        return await DetailedActivitiesFetcher(self.api_async).fetch_activity_data(
            keys=keys, previuos_week=previous_week
        )
