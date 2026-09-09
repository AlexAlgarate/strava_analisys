import asyncio
from collections.abc import Mapping
from typing import cast

import pandas as pd

from src.core.ports.strava import StravaAPI
from src.core.streams.processor import process_streams


class ActivityStreamsFetcher:
    """Fetches activity stream data from Strava API."""

    def __init__(self, api: StravaAPI, activity_id: int | None = None) -> None:
        self._api = api
        self._activity_id = activity_id

    async def fetch_activity_data(self, stream_keys: list[str]) -> pd.DataFrame:
        """Fetch stream data for a single activity.

        Args:
            stream_keys: List of stream types to fetch (e.g., time, distance, heartrate)

        Returns:
            DataFrame containing the stream data

        Raises:
            ValueError: If no activity ID is provided
        """
        if not self._activity_id:
            raise ValueError("Activity ID is required for this operation.")
        params = {"keys": ",".join(stream_keys), "key_by_type": "true"}
        response = await self._api.make_request(
            f"/activities/{self._activity_id}/streams", params
        )
        if not isinstance(response, Mapping):
            raise TypeError("Strava streams response must be an object.")
        return process_streams(
            response=cast(dict[str, object], response),
            id_activity=self._activity_id,
        )

    @classmethod
    async def fetch_multiple_activities_streams(
        cls,
        api: StravaAPI,
        list_id_activities: list[int],
        stream_keys: list[str],
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
            cls(api=api, activity_id=activity_id).fetch_activity_data(
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
