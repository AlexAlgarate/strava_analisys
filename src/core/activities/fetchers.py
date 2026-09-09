import asyncio
import logging
from collections.abc import Sequence
from typing import cast

from src.core.ports.export import ActivityDetailsWriter
from src.core.ports.strava import StravaAPI
from src.utils.helpers import get_week_epoch_range

ActivityData = dict[str, object]

logger = logging.getLogger(__name__)


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
    """Fetch selected fields from every activity in a week."""

    def __init__(
        self,
        api: StravaAPI,
        writer: ActivityDetailsWriter | None = None,
    ) -> None:
        self._api = api
        self._writer = writer

    async def fetch_activity_data(
        self,
        keys: Sequence[str],
        previous_week: bool = False,
    ) -> list[ActivityData]:
        activities = await WeeklyActivitiesFetcher(self._api).fetch_activity_data(
            previous_week=previous_week
        )
        if not activities:
            raise ValueError("No activities found.")

        activity_ids = [self._get_activity_id(activity) for activity in activities]
        detailed_activities = await self._fetch_all_activity_details(activity_ids)
        if self._writer is not None:
            self._writer.write(detailed_activities)

        return [
            self._filter_activity_keys(activity, keys)
            for activity in detailed_activities
        ]

    async def _fetch_all_activity_details(
        self, activity_ids: Sequence[int]
    ) -> list[ActivityData]:
        results = await asyncio.gather(
            *(
                self._api.make_request(f"/activities/{activity_id}")
                for activity_id in activity_ids
            ),
            return_exceptions=True,
        )

        activities: list[ActivityData] = []
        for activity_id, result in zip(activity_ids, results, strict=True):
            if isinstance(result, asyncio.CancelledError):
                raise result
            if isinstance(result, BaseException):
                logger.warning(
                    "Could not fetch Strava activity %s: %s",
                    activity_id,
                    result,
                )
                activities.append({})
                continue
            try:
                activities.append(_parse_activity(result))
            except TypeError:
                logger.warning(
                    "Strava returned invalid detail data for activity %s",
                    activity_id,
                )
                activities.append({})
        return activities

    @staticmethod
    def _get_activity_id(activity: ActivityData) -> int:
        activity_id = activity.get("id")
        if isinstance(activity_id, bool) or not isinstance(activity_id, int):
            raise TypeError("An activity must contain an integer id.")
        return activity_id

    @staticmethod
    def _filter_activity_keys(
        activity: ActivityData, keys: Sequence[str]
    ) -> ActivityData:
        return {key: activity[key] for key in keys if key in activity}


def _parse_activity_list(value: object) -> list[ActivityData]:
    if not isinstance(value, list):
        raise TypeError("Strava activities response must be a list.")
    return [_parse_activity(item) for item in value]


def _parse_activity(value: object) -> ActivityData:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise TypeError("A Strava activity must be an object with string keys.")
    return cast(ActivityData, value)
