from typing import Any, Dict

from src.activities import (
    GetActivityDetails,
    GetActivityRange,
    GetLast200Activities,
    GetOneActivity,
    GetStreamsActivities,
)
from src.strava_api.api_requests.async_request import AsyncStravaAPI
from src.strava_api.api_requests.sync_request import SyncStravaAPI
from src.utils import constants as constant


class StravaService:
    def __init__(self, api_sync: SyncStravaAPI, api_async: AsyncStravaAPI):
        self.api_sync = api_sync
        self.api_async = api_async

    async def get_streams_for_activity(self, activity_id: int) -> Dict[str, Any]:
        return await GetStreamsActivities(
            api=self.api_async, id_activity=activity_id
        ).fetch_activity_data(stream_keys=constant.ACTIVITY_STREAMS_KEYS)

    async def get_streams_for_multiple_activities(
        self, activity_ids: list[int]
    ) -> Dict[str, Any]:
        return await GetStreamsActivities.fetch_multiple_activities_streams(
            api=self.api_async,
            list_id_activities=activity_ids,
            stream_keys=constant.ACTIVITY_STREAMS_KEYS,
        )

    async def get_activity_range(self, previous_week: bool = False) -> Dict[str, Any]:
        return await GetActivityRange(self.api_async).fetch_activity_data(
            previous_week=previous_week
        )

    async def get_activity_details(self, previous_week: bool = False) -> Dict[str, Any]:
        return await GetActivityDetails(self.api_async).fetch_activity_data(
            keys=constant.ACTIVITY_DETAILED_KEYS, previuos_week=previous_week
        )

    def get_one_activity(self, activity_id: int) -> Dict[str, Any]:
        return GetOneActivity(
            api=self.api_sync, id_activity=activity_id
        ).fetch_activity_data()

    def get_last_200_activities(self) -> Dict[str, Any]:
        return GetLast200Activities(self.api_sync).fetch_activity_data()
