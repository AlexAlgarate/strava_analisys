from typing import Any, Dict

from src.activities.detailed_activities import (
    DetailedActivitiesFetcher,
    WeeklyActivitiesFetcher,
)
from src.activities.get_streams import ActivityStreamsFetcher
from src.activities.last_200_activities import RecentActivitiesFetcher
from src.activities.one_activity import SingleActivityFetcher
from src.strava_api.api_requests.async_request import AsyncStravaAPI
from src.strava_api.api_requests.sync_request import SyncStravaAPI
from src.utils import constants as constant


class StravaService:
    def __init__(self, api_sync: SyncStravaAPI, api_async: AsyncStravaAPI):
        self.api_sync = api_sync
        self.api_async = api_async

    async def get_streams_for_activity(self, activity_id: int) -> Dict[str, Any]:
        return await ActivityStreamsFetcher(
            api=self.api_async, id_activity=activity_id
        ).fetch_activity_data(stream_keys=constant.ACTIVITY_STREAMS_KEYS)

    async def get_streams_for_multiple_activities(
        self, activity_ids: list[int]
    ) -> Dict[str, Any]:
        return await ActivityStreamsFetcher.fetch_multiple_activities_streams(
            api=self.api_async,
            list_id_activities=activity_ids,
            stream_keys=constant.ACTIVITY_STREAMS_KEYS,
        )

    async def get_activity_range(self, previous_week: bool = False) -> Dict[str, Any]:
        return await WeeklyActivitiesFetcher(self.api_async).fetch_activity_data(
            previous_week=previous_week
        )

    async def get_activity_details(self, previous_week: bool = False) -> Dict[str, Any]:
        keys = [key.value for key in constant.ActivityDetailKey]
        return await DetailedActivitiesFetcher(self.api_async).fetch_activity_data(
            keys=keys, previuos_week=previous_week
        )

    def get_one_activity(self, activity_id: int) -> Dict[str, Any]:
        return SingleActivityFetcher(
            api=self.api_sync, id_activity=activity_id
        ).fetch_activity_data()

    def get_last_200_activities(self) -> Dict[str, Any]:
        return RecentActivitiesFetcher(self.api_sync).fetch_activity_data()
