import asyncio
from typing import List

import pandas as pd

from src.interfaces.activities import InterfaceActivitiesStrava
from src.interfaces.strava_api import AsyncStravaAPI
from src.utils import helpers as helper


class ActivityStreamsFetcher(InterfaceActivitiesStrava):
    async def fetch_activity_data(self, stream_keys: List[str]) -> pd.DataFrame:
        if not self.id_activity:
            raise ValueError("Activity ID is required for this operation.")
        params = {"keys": ",".join(stream_keys), "key_by_type": "true"}
        response_json = await self.api.make_request_async(
            f"/activities/{self.id_activity}/streams", params
        )
        return helper.process_streams(
            response=response_json, id_activity=self.id_activity
        )

    @classmethod
    @helper.func_time_execution
    async def fetch_multiple_activities_streams(
        cls, api: AsyncStravaAPI, list_id_activities: List[int], stream_keys: List[str]
    ) -> pd.DataFrame:
        tasks = [
            cls(api=api, id_activity=activity_id).fetch_activity_data(
                stream_keys=stream_keys
            )
            for activity_id in list_id_activities
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        processed_results = [
            result for result in results if isinstance(result, pd.DataFrame)
        ]
        return (
            pd.concat(processed_results, ignore_index=True)
            if processed_results
            else pd.DataFrame()
        )

    # TODO: Fix Streams Data Extraction
    # class Activity:
    #     ZONES_KEY = [
    #         "Zone_1",
    #         "Zone_2",
    #         "Zone_3",
    #         "Zone_4",
    #         "Zone_5",
    #     ]

    """

        def get_activities_zones(self, save_zones: bool = False) -> Dict:
            if not self.id_activity:
                raise ValueError("Activity ID is required for this operation.")
            response_zones = self.api.make_request(f"/activities/{self.id_activity}/zones")
            zones = response_zones.get("distribution_buckets")
            if zones is None:
                raise ValueError("The activity does not have heartrate information.")

            zones_dict = dict(zip(self.ZONES_KEY, zones))
            if save_zones:
                if not helper.check_path("json_zones_files/"):
                    self.logger.info("\nCreating folder...")
                file_path = f"json_zones_files/zones_{self.id_activity}.json"
                with open(file_path, "w") as f:
                    json.dump(zones_dict, f, indent=4)

            return zones_dict
    """
