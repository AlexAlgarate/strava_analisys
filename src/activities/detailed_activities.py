import asyncio
from typing import List

from src.interfaces.activities import InterfaceActivitiesStrava
from src.utils import helpers as helper


class WeeklyActivitiesFetcher(InterfaceActivitiesStrava):
    @helper.func_time_execution
    async def fetch_activity_data(self, previous_week: bool = False) -> List[dict]:
        monday, sunday = helper.get_epoch_times_for_week(previous_week=previous_week)
        params = {
            "per_page": 200,
            "page": 1,
            "after": str(monday),
            "before": str(sunday),
        }
        return await self.api.make_request_async(endpoint="/activities", params=params)


class DetailedActivitiesFetcher(InterfaceActivitiesStrava):
    async def fetch_activity_data(
        self, keys: List[str], previuos_week: bool = False
    ) -> List[dict]:
        activities = await WeeklyActivitiesFetcher(self.api).fetch_activity_data(
            previous_week=previuos_week
        )
        if not activities:
            raise ValueError("No activities found.")

        activity_ids = [activity["id"] for activity in activities]
        detailed_activity = await self._fetch_all_activity_details(activity_ids)

        return [
            self._filter_activity_keys(activity, keys) for activity in detailed_activity
        ]

    async def _fetch_all_activity_details(self, activity_ids: List[int]) -> List[dict]:
        tasks = [
            self._get_activity_details(activity_id) for activity_id in activity_ids
        ]
        return await asyncio.gather(*tasks)

    async def _get_activity_details(self, activity_id: int) -> dict:
        try:
            return await self.api.make_request_async(f"/activities/{activity_id}")
        except Exception as e:
            print(f"⚠️ Error fetching activity {activity_id}: {e}")
            return {}

    @staticmethod
    def _filter_activity_keys(activity: dict, keys: List[str]) -> dict:
        return {k: activity[k] for k in keys if k in activity}
