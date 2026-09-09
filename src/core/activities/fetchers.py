import asyncio
from typing import cast

from src.core.ports.strava import StravaAPI
from src.domain.detailed_activity import DetailedActivity
from src.utils.helpers import get_week_epoch_range

ActivityData = dict[str, object]


class WeeklyActivitiesFetcher:
    """Fetch activities belonging to the current or previous week."""

    def __init__(self, api: StravaAPI) -> None:
        self._api = api

    async def fetch_activity_data(
        self, previous_week: bool = False
    ) -> list[ActivityData]:
        monday, sunday = get_week_epoch_range(previous_week=previous_week)
        response = await self._api.make_request(
            endpoint="/activities",
            params={
                "per_page": 200,
                "page": 1,
                "after": str(monday),
                "before": str(sunday),
            },
        )
        return _parse_activity_list(response)


class DetailedActivitiesFetcher:
    """Fetch and validate every detailed activity in a week."""

    def __init__(self, api: StravaAPI) -> None:
        self._api = api

    async def fetch_activity_data(
        self,
        previous_week: bool = False,
    ) -> list[DetailedActivity]:
        activities = await WeeklyActivitiesFetcher(self._api).fetch_activity_data(
            previous_week=previous_week
        )
        if not activities:
            raise ValueError("No activities found.")

        activity_ids = [self._get_activity_id(activity) for activity in activities]
        return await self._fetch_all_activity_details(activity_ids)

    async def _fetch_all_activity_details(
        self, activity_ids: list[int]
    ) -> list[DetailedActivity]:
        results = await asyncio.gather(
            *(
                self._api.make_request(f"/activities/{activity_id}")
                for activity_id in activity_ids
            )
        )
        return [
            DetailedActivity.from_mapping(_parse_activity(result)) for result in results
        ]

    @staticmethod
    def _get_activity_id(activity: ActivityData) -> int:
        activity_id = activity.get("id")
        if isinstance(activity_id, bool) or not isinstance(activity_id, int):
            raise TypeError("An activity must contain an integer id.")
        return activity_id


def _parse_activity_list(value: object) -> list[ActivityData]:
    if not isinstance(value, list):
        raise TypeError("Strava activities response must be a list.")
    return [_parse_activity(item) for item in value]


def _parse_activity(value: object) -> ActivityData:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise TypeError("A Strava activity must be an object with string keys.")
    return cast(ActivityData, value)
