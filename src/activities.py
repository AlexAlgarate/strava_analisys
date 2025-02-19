import asyncio
import json
from abc import ABC, abstractmethod
from typing import Dict, List

import pandas as pd

from src.strava_api import InterfaceStravaAPI, StravaAPI
from src.utils.helpers import (
    Logger,
    check_path,
    func_time_execution,
    get_epoch_times_for_week,
    process_streams,
)


class InterfaceActivitiesStrava(ABC):
    def __init__(self, api: InterfaceStravaAPI, id_activity: int = None):
        self.api = api
        self.id_activity = id_activity
        self.logger = Logger().setup_logger()

    @abstractmethod
    def fetch_activity_data(self, *args, **kwargs):
        pass


class GetOneActivity(InterfaceActivitiesStrava):
    def fetch_activity_data(self) -> dict:
        if not self.id_activity:
            raise ValueError("Activity ID is required for this operation.")
        return self.api.make_request(f"/activities/{self.id_activity}")


class GetLast200Activities(InterfaceActivitiesStrava):
    def fetch_activity_data(self) -> dict:
        params = {"per_page": 200, "page": 1}
        return self.api.make_request(endpoint="/activities", params=params)


class GetActivityRange(InterfaceActivitiesStrava):
    @func_time_execution
    async def fetch_activity_data(self, previous_week: bool = False) -> List[dict]:
        monday, sunday = get_epoch_times_for_week(previous_week=previous_week)
        params = {
            "per_page": 200,
            "page": 1,
            "after": str(monday),
            "before": str(sunday),
        }
        return await self.api.make_request_async(endpoint="/activities", params=params)


class GetActivityDetails(InterfaceActivitiesStrava):
    async def fetch_activity_data(
        self, keys: List[str], previuos_week: bool = False
    ) -> List[dict]:
        activities = await GetActivityRange(self.api).fetch_activity_data(
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
        """Fetch detailed data for multiple activities asynchronously."""
        tasks = [
            self._get_activity_details(activity_id) for activity_id in activity_ids
        ]
        return await asyncio.gather(*tasks)

    async def _get_activity_details(self, activity_id: int) -> dict:
        """Fetch detailed data for a single activity."""
        try:
            return self.api.make_request(f"/activities/{activity_id}")
        except Exception as e:
            print(f"⚠️ Error fetching activity {activity_id}: {e}")
            return {}

    @staticmethod
    def _filter_activity_keys(activity: dict, keys: List[str]) -> dict:
        """Filter only the selected keys from an activity dictionary."""
        return {k: activity[k] for k in keys if k in activity}


class Activity:
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
        self.logger = Logger().setup_logger()

    def get_one_activity_detailed(self, id_activity: int, keys: List[str]) -> dict:
        activities = self.api.make_request(f"/activities/{id_activity}")
        id_activities = [activity["id"] for activity in activities]
        results = []
        for id in id_activities:
            detailed_activity = self.get_one_activity(id)
            activity_details = {k: detailed_activity[k] for k in keys}
            results.append(activity_details)
        return results

    def get_activity_range(self, previous_week: bool = False) -> List[dict]:
        monday, sunday = get_epoch_times_for_week(previous_week=previous_week)
        params = {
            "per_page": 200,
            "page": 1,
            "after": str(monday),
            "before": str(sunday),
        }
        return self.api.make_request("/activities", params)

    @func_time_execution
    async def get_activity_range_async(self, previous_week: bool = False) -> List[dict]:
        monday, sunday = get_epoch_times_for_week(previous_week=previous_week)
        params = {
            "per_page": 200,
            "page": 1,
            "after": str(monday),
            "before": str(sunday),
        }
        return await self.api.make_request_async("/activities", params)

    def get_one_activity():
        pass

    def get_detailed_activity_range(
        self, keys: List[str], previous_week: bool = False
    ) -> List[dict]:
        monday, sunday = get_epoch_times_for_week(previous_week=previous_week)
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

    def get_activities_zones(self, save_zones: bool = False) -> Dict:
        if not self.id_activity:
            raise ValueError("Activity ID is required for this operation.")
        response_zones = self.api.make_request(f"/activities/{self.id_activity}/zones")
        zones = response_zones.get("distribution_buckets")
        if zones is None:
            raise ValueError("The activity does not have heartrate information.")

        zones_dict = dict(zip(self.ZONES_KEY, zones))
        if save_zones:
            if not check_path("json_zones_files/"):
                self.logger.info("\nCreating folder...")
            file_path = f"json_zones_files/zones_{self.id_activity}.json"
            with open(file_path, "w") as f:
                json.dump(zones_dict, f, indent=4)

        return zones_dict

    async def get_streams_asyncio(self, stream_keys: List[str]) -> pd.DataFrame:
        if not self.id_activity:
            raise ValueError("Activity ID is required for this operation.")
        params = {"keys": ",".join(stream_keys), "key_by_type": "true"}
        response_json = await self.api.make_request_async(
            f"/activities/{self.id_activity}/streams", params
        )
        return process_streams(response_json, self.id_activity)

    @classmethod
    @func_time_execution
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
