import asyncio
from typing import List

import pandas as pd

from src.core.streams.processor import process_streams
from src.infrastructure.api_clients.async_strava_api import AsyncStravaAPI
from src.interfaces.activities import IActivityFetcher


class ActivityStreamsFetcher(IActivityFetcher):
    """Fetches activity stream data from Strava API."""

    async def fetch_activity_data(self, stream_keys: List[str]) -> pd.DataFrame:
        """Fetch stream data for a single activity.

        Args:
            stream_keys: List of stream types to fetch (e.g., time, distance, heartrate)

        Returns:
            DataFrame containing the stream data

        Raises:
            ValueError: If no activity ID is provided
        """
        if not self.id_activity:
            raise ValueError("Activity ID is required for this operation.")
        params = {"keys": ",".join(stream_keys), "key_by_type": "true"}
        response_json = await self.api.make_request(
            f"/activities/{self.id_activity}/streams", params
        )
        return process_streams(
            response=response_json, id_activity=self.id_activity
        )

    @classmethod
    async def fetch_multiple_activities_streams(
        cls,
        api: AsyncStravaAPI,
        list_id_activities: List[int],
        stream_keys: List[str],
    ) -> pd.DataFrame:
        """Fetch stream data for multiple activities in parallel.

        Args:
            api: Strava API client
            list_id_activities: List of activity IDs to fetch streams for
            stream_keys: List of stream types to fetch

        Returns:
            DataFrame containing concatenated stream data from all activities
        """
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
