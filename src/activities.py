import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

import aiohttp
import pandas as pd
import requests

from src import utils as utils

logger = utils.Logger().setup_logger()


class ActivitiesManager:
    BASE_URL = "https://www.strava.com/api/v3"
    ZONES_KEY = [
        "Zone_1",
        "Zone_2",
        "Zone_3",
        "Zone_4",
        "Zone_5",
    ]

    def __init__(self, access_token: str, id_activity: int = None):
        if not access_token:
            raise ValueError("Access token must be provided.")
        self.access_token = access_token
        self.id_activity = id_activity

    def _get_headers(self) -> Dict[str, str]:
        """Generate headers for requests."""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    def _get_url(self, endpoint: str) -> str:
        """Construct full URL for a given endpoint."""
        return f"{self.BASE_URL}{endpoint}"

    def _make_request(self, url: str, params: dict = None) -> dict:
        try:
            response = requests.get(url, headers=self._get_headers(), params=params)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Error making request to {url}: {e}")
            return {}

    def get_one_activity(self, id_activity: int) -> dict:
        url = self._get_url(f"/activities/{id_activity}")
        return self._make_request(url)

    def get_last_200_activities(self) -> List[Dict]:
        """Fetch the last 200 activities for the authenticated user."""
        url = self._get_url("/activities")
        params = {"per_page": 200, "page": 1}
        return self._make_request(url, params)

    @staticmethod
    def get_epoch_times_for_week(previous_week: bool = False) -> tuple:
        today = datetime.today()
        _iso_year, _iso_week, iso_weekday = today.isocalendar()
        days_offset = -iso_weekday + 1 - (7 if previous_week else 0)

        start_of_week = today + timedelta(days=days_offset)
        end_of_week = start_of_week + timedelta(days=6)

        start_of_week_epoch = int(
            start_of_week.replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
        )

        end_of_week_epoch = int(
            end_of_week.replace(
                hour=23, minute=59, second=59, microsecond=999999
            ).timestamp()
        )

        return start_of_week_epoch, end_of_week_epoch

    def get_activity_range(self, previous_week: bool = False) -> List[dict]:
        url = self._get_url("/activities")
        monday, sunday = self.get_epoch_times_for_week(previous_week=previous_week)
        params = {
            "per_page": 200,
            "page": 1,
            "after": str(monday),
            "before": str(sunday),
        }

        return self._make_request(url, params)

    def get_detailed_activity_range(
        self, keys: List[str], previous_week: bool = False
    ) -> List[dict]:
        url = self._get_url("/activities")
        monday, sunday = self.get_epoch_times_for_week(previous_week=previous_week)
        params = {
            "per_page": 200,
            "page": 1,
            "after": str(monday),
            "before": str(sunday),
        }

        activities = self._make_request(url, params)
        id_activities = [activity_id["id"] for activity_id in activities]
        results = []

        detailed_activities = map(self.get_one_activity, id_activities)

        for detailed_activity in detailed_activities:
            activity_details = {}
            for k in keys:
                activity_details[k] = detailed_activity[k]
            results.append(activity_details)

        return results

    def get_one_activity_detailed(self, id_activity: int, keys: List[str]) -> dict:
        url = self._get_url(f"/activities/{id_activity}")
        activities = self._make_request(url)

        id_activities = [activity_id["id"] for activity_id in activities]
        results = []
        for id in id_activities:
            detailed_activity = self.get_one_activity(id)
            activity_details = {}
            for k in keys:
                activity_details[k] = detailed_activity[k]
            results.append(activity_details)
        return results

    @staticmethod
    def _check_path(target_path: str) -> bool:
        execution_path = Path(__file__).parent
        target_directory = execution_path / target_path
        if not target_directory.exists():
            target_directory.mkdir(parents=True, exist_ok=True)
        return target_directory.is_dir()

    def get_activities_zones(self, save_zones: bool = False) -> Dict:
        """Fetch activity zones for a specific activity."""
        if not self.id_activity:
            raise ValueError("Activity ID is required for this operation.")
        url = f"https://www.strava.com/activities/{str(self.id_activity)}/zones"

        response_zones = self._make_request(url)
        zones = response_zones.get("distribution_buckets")
        if zones is None:
            raise ValueError("The activity does not have heartrate information.")

        zones_dict = dict(zip(self.ZONES_KEY, zones))
        if save_zones:
            if not self._check_path("json_zones_files/"):
                logger.info("\nCreating folder...")
            file_path = f"json_zones_files/zones_{self.id_activity}.json"
            with open(file_path, "w") as f:
                json.dump(zones_dict, f, indent=4)

        return zones_dict

    @staticmethod
    def _process_streams(response: Dict, id_activity: int) -> pd.DataFrame:
        """Transform API response into a structured DataFrame."""
        data = {
            stream_type: stream_data.get("data", [])
            for stream_type, stream_data in response.items()
        }
        df = pd.DataFrame(data)
        df["id"] = id_activity
        return df

    async def get_streams_asyncio(self, stream_keys: List[str]) -> pd.DataFrame:
        """Fetch activity streams asynchronously."""
        if not self.id_activity:
            raise ValueError("Activity ID is required for this operation.")
        url = self._get_url(f"/activities/{self.id_activity}/streams")
        params = {"keys": ",".join(stream_keys), "key_by_type": "true"}
        async with aiohttp.ClientSession(headers=self._get_headers()) as session:
            async with session.get(url, params=params) as response:
                if response.status == 429:
                    raise Exception("Too Many Requests. Wait and try again later.")
                response.raise_for_status()
                response_json = await response.json()
                return self._process_streams(response_json, self.id_activity)

    @classmethod
    async def get_multiple_activities_streams(
        cls, access_token: str, list_id_activities: List[int], stream_keys: List[str]
    ) -> pd.DataFrame:
        """Fetch streams for multiple activities concurrently."""
        tasks = [
            cls(access_token, activity_id).get_streams_asyncio(stream_keys)
            for activity_id in list_id_activities
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        # Handle exceptions for individual tasks
        processed_results = [
            result for result in results if isinstance(result, pd.DataFrame)
        ]
        return pd.concat(processed_results, ignore_index=True)

    @classmethod
    @utils.func_time_execution
    async def get_all_streams(
        cls, access_token: str, list_id_activities: List[int], stream_keys: List[str]
    ) -> pd.DataFrame:
        """Wrapper method to fetch all streams."""
        return await cls.get_multiple_activities_streams(
            access_token, list_id_activities, stream_keys
        )


"""
from datetime import datetime, timedelta
from typing import List, Dict


class ActivityFetcher:
    @utils.calculate_time
    async def get_detailed_activity_range(
        self, keys: List[str], previous_week: bool = False
    ) -> List[dict]:
        monday, sunday = self.get_epoch_times_for_week(previous_week)
        activities = await self.fetch_activities(monday, sunday)

        detailed_activities = await self.fetch_detailed_activities(activities, keys)
        return detailed_activities

    @staticmethod
    def get_epoch_times_for_week(previous_week: bool = False) -> tuple:
        today = datetime.today()
        _iso_year, _iso_week, iso_weekday = today.isocalendar()
        days_offset = -iso_weekday + 1 - (7 if previous_week else 0)

        start_of_week = today + timedelta(days=days_offset)
        end_of_week = start_of_week + timedelta(days=6)

        start_of_week_epoch = int(start_of_week.replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
        end_of_week_epoch = int(end_of_week.replace(hour=23, minute=59, second=59, microsecond=999999).timestamp())

        return start_of_week_epoch, end_of_week_epoch

    async def fetch_activities(self, monday: int, sunday: int) -> List[dict]:
        url = self._get_url("/activities")
        params = {
            "per_page": 200,
            "page": 1,
            "after": str(monday),
            "before": str(sunday),
        }
        return await self._make_request(url, params)

    async def fetch_detailed_activities(self, activities: List[dict], keys: List[str]) -> List[dict]:
        id_activities = [activity["id"] for activity in activities]
        activity_details = await asyncio.gather(
            *[self.get_activity_details(id_activity, keys) for id_activity in id_activities]
        )
        return activity_details

    async def get_activity_details(self, id_activity: int, keys: List[str]) -> dict:
        detailed_activity = await self.get_one_activity(id_activity)
        return {k: detailed_activity[k] for k in keys}

    async def get_one_activity(self, id_activity: int) -> dict:
        url = self._get_url(f"/activities/{id_activity}")
        return await self._make_request(url)

    async def _make_request(self, url: str, params: dict = None) -> dict:
        try:
            response = await self._async_get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error making request to {url}: {e}")
            return {}

    async def _async_get(self, url: str, params: dict = None):
        # You may want to replace this with your actual async request code (e.g., using `aiohttp`)
        return requests.get(url, params=params)  # Blocking for now, replace with async

"""
