from collections.abc import Mapping
from typing import cast

from src.core.concurrency import DEFAULT_MAX_CONCURRENCY, map_concurrently
from src.core.ports.strava import StravaAPI
from src.domain.detailed_activity import DetailedActivity
from src.utils.helpers import get_week_epoch_range

ACTIVITIES_PAGE_SIZE = 200


class WeeklyActivitiesFetcher:
    """Fetch activities belonging to the current or previous week."""

    def __init__(self, api: StravaAPI) -> None:
        self._api = api

    async def fetch_activity_data(
        self, previous_week: bool = False
    ) -> list[DetailedActivity]:
        monday, sunday = get_week_epoch_range(previous_week=previous_week)
        activities: list[DetailedActivity] = []
        page = 1

        while True:
            response = await self._api.make_request(
                endpoint="/activities",
                params={
                    "per_page": ACTIVITIES_PAGE_SIZE,
                    "page": page,
                    "after": str(monday),
                    "before": str(sunday),
                },
            )
            page_items = _parse_activity_list(response)
            activities.extend(
                DetailedActivity.from_mapping(item) for item in page_items
            )
            if len(page_items) < ACTIVITIES_PAGE_SIZE:
                return activities
            page += 1


class DetailedActivitiesFetcher:
    """Fetch and validate every detailed activity in a week."""

    def __init__(
        self,
        api: StravaAPI,
        *,
        max_concurrency: int = DEFAULT_MAX_CONCURRENCY,
    ) -> None:
        self._api = api
        self._max_concurrency = max_concurrency

    async def fetch_activity_data(
        self,
        previous_week: bool = False,
    ) -> list[DetailedActivity]:
        activities = await WeeklyActivitiesFetcher(self._api).fetch_activity_data(
            previous_week=previous_week
        )
        if not activities:
            raise ValueError("No activities found.")

        activity_ids = [activity.id for activity in activities]
        return await self._fetch_all_activity_details(activity_ids)

    async def _fetch_all_activity_details(
        self, activity_ids: list[int]
    ) -> list[DetailedActivity]:
        results = await map_concurrently(
            activity_ids,
            self._fetch_activity_details,
            max_concurrency=self._max_concurrency,
        )
        return [
            DetailedActivity.from_mapping(_parse_activity(result)) for result in results
        ]

    async def _fetch_activity_details(self, activity_id: int) -> object:
        return await self._api.make_request(f"/activities/{activity_id}")


def _parse_activity_list(value: object) -> list[Mapping[str, object]]:
    if not isinstance(value, list):
        raise TypeError("Strava activities response must be a list.")
    return [_parse_activity(item) for item in value]


def _parse_activity(value: object) -> Mapping[str, object]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise TypeError("A Strava activity must be an object with string keys.")
    return cast(dict[str, object], value)
