import asyncio
import json
from typing import Dict, List

import pandas as pd

from src import utils as utils
from src.strava_api import StravaAPI


class ActivitiesManager:
    ZONES_KEY = [
        "Zone_1",
        "Zone_2",
        "Zone_3",
        "Zone_4",
        "Zone_5",
    ]

    def __init__(self, access_token: str, id_activity: int = None):
        self.api = StravaAPI(access_token)
        self.id_activity = id_activity
        self.logger = utils.Logger().setup_logger()

    def get_one_activity(self, id_activity: int) -> dict:
        return self.api.make_request(f"/activities/{id_activity}")

    def get_last_200_activities(self) -> List[Dict]:
        """Fetch the last 200 activities for the authenticated user."""
        params = {"per_page": 200, "page": 1}
        return self.api.make_request("/activities", params)

    def get_activity_range(self, previous_week: bool = False) -> List[dict]:
        monday, sunday = utils.get_epoch_times_for_week(previous_week=previous_week)
        params = {
            "per_page": 200,
            "page": 1,
            "after": str(monday),
            "before": str(sunday),
        }
        return self.api.make_request("/activities", params)

    @utils.func_time_execution
    async def get_activity_range_async(self, previous_week: bool = False) -> List[dict]:
        monday, sunday = utils.get_epoch_times_for_week(previous_week=previous_week)
        params = {
            "per_page": 200,
            "page": 1,
            "after": str(monday),
            "before": str(sunday),
        }
        return await self.api.make_request_async("/activities", params)

    def get_detailed_activity_range(
        self, keys: List[str], previous_week: bool = False
    ) -> List[dict]:
        monday, sunday = utils.get_epoch_times_for_week(previous_week=previous_week)
        params = {
            "per_page": 200,
            "page": 1,
            "after": str(monday),
            "before": str(sunday),
        }

        activities = self.api.make_request("/activities", params)
        id_activities = [activity["id"] for activity in activities]
        results = []

        detailed_activities = map(self.get_one_activity, id_activities)

        for detailed_activity in detailed_activities:
            activity_details = {k: detailed_activity[k] for k in keys}
            results.append(activity_details)

        return results

    def get_one_activity_detailed(self, id_activity: int, keys: List[str]) -> dict:
        activities = self.api.make_request(f"/activities/{id_activity}")
        id_activities = [activity["id"] for activity in activities]
        results = []
        for id in id_activities:
            detailed_activity = self.get_one_activity(id)
            activity_details = {k: detailed_activity[k] for k in keys}
            results.append(activity_details)
        return results

    def get_activities_zones(self, save_zones: bool = False) -> Dict:
        """Fetch activity zones for a specific activity."""
        if not self.id_activity:
            raise ValueError("Activity ID is required for this operation.")
        response_zones = self.api.make_request(f"/activities/{self.id_activity}/zones")
        zones = response_zones.get("distribution_buckets")
        if zones is None:
            raise ValueError("The activity does not have heartrate information.")

        zones_dict = dict(zip(self.ZONES_KEY, zones))
        if save_zones:
            if not utils.check_path("json_zones_files/"):
                self.logger.info("\nCreating folder...")
            file_path = f"json_zones_files/zones_{self.id_activity}.json"
            with open(file_path, "w") as f:
                json.dump(zones_dict, f, indent=4)

        return zones_dict

    async def get_streams_asyncio(self, stream_keys: List[str]) -> pd.DataFrame:
        """Fetch activity streams asynchronously."""
        if not self.id_activity:
            raise ValueError("Activity ID is required for this operation.")
        params = {"keys": ",".join(stream_keys), "key_by_type": "true"}
        response_json = await self.api.make_request_async(
            f"/activities/{self.id_activity}/streams", params
        )
        return utils.process_streams(response_json, self.id_activity)

    @classmethod
    @utils.func_time_execution
    async def get_multiple_activities_streams(
        cls, access_token: str, list_id_activities: List[int], stream_keys: List[str]
    ) -> pd.DataFrame:
        """Fetch streams for multiple activities concurrently."""
        tasks = [
            cls(access_token, activity_id).get_streams_asyncio(stream_keys)
            for activity_id in list_id_activities
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        processed_results = [
            result for result in results if isinstance(result, pd.DataFrame)
        ]
        return pd.concat(processed_results, ignore_index=True)
