import json
import os
from typing import Dict

from src.infrastructure.api_clients.async_strava_api import AsyncStravaAPI
from src.utils.helpers import check_path


class ActivityZones:
    ZONES_KEY = ["Zone_1", "Zone_2", "Zone_3", "Zone_4", "Zone_5"]

    def __init__(self, api: AsyncStravaAPI, id_activity: int | None):
        self.api = api
        self.id_activity = id_activity

    async def get_zones(self, save_zones: bool = False) -> Dict[str, int]:
        if not self.id_activity:
            raise ValueError("Activity ID is required for this operation.")

        response_zones = await self.api.make_request(
            f"/activities/{self.id_activity}/zones"
        )
        zones = response_zones.get("distribution_buckets")

        if zones is None:
            raise ValueError("The activity does not have heartrate information.")

        zones_dict = dict(zip(self.ZONES_KEY, zones))
        if save_zones:
            await self._save_zones_to_file(zones_dict)

        return zones_dict

    async def _save_zones_to_file(self, zones_dict: Dict[str, int]) -> None:
        if not check_path("json_zones_files/"):
            os.makedirs("json_zones_files/")

        file_path = f"json_zones_files/zones_{self.id_activity}.json"
        with open(file_path, "w") as f:
            json.dump(zones_dict, f, indent=4)
