from collections.abc import Callable

from src.application.errors import InvalidExternalDataError
from src.domain.activity_id import require_activity_id
from src.domain.activity_stream import ActivityStream
from src.domain.detailed_activity import DetailedActivity
from src.domain.heart_rate_zones import HeartRateZones
from src.domain.week_period import WeekPeriod
from src.infrastructure.api_clients.async_strava_api import AsyncStravaAPI
from src.infrastructure.strava.activity_mapper import map_activity, map_activity_list
from src.infrastructure.strava.heart_rate_zone_mapper import map_heart_rate_zones
from src.infrastructure.strava.stream_mapper import map_activity_stream

MAX_PAGE_SIZE = 200
DEFAULT_PAGE_SIZE = MAX_PAGE_SIZE
DEFAULT_MAX_PAGES = 100
STREAM_KEYS = ("time", "distance", "heartrate")
ATHLETE_ACTIVITIES_ENDPOINT = "/athlete/activities"


class StravaActivityGateway:
    """Adapt Strava's HTTP API to the domain-oriented activity gateway."""

    def __init__(
        self,
        api: AsyncStravaAPI,
        *,
        page_size: int = DEFAULT_PAGE_SIZE,
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> None:
        if isinstance(page_size, bool) or not isinstance(page_size, int):
            raise TypeError("Activity page size must be an integer.")
        if page_size < 1:
            raise ValueError("Activity page size must be at least one.")
        if page_size > MAX_PAGE_SIZE:
            raise ValueError(
                f"Activity page size cannot exceed Strava's limit of {MAX_PAGE_SIZE}."
            )
        if isinstance(max_pages, bool) or not isinstance(max_pages, int):
            raise TypeError("Maximum activity pages must be an integer.")
        if max_pages < 1:
            raise ValueError("Maximum activity pages must be at least one.")
        self._api = api
        self._page_size = page_size
        self._max_pages = max_pages

    async def list_activities(self, period: WeekPeriod) -> list[DetailedActivity]:
        activities: list[DetailedActivity] = []
        for page in range(1, self._max_pages + 1):
            response = await self._api.make_request(
                endpoint=ATHLETE_ACTIVITIES_ENDPOINT,
                params={
                    "per_page": self._page_size,
                    "page": page,
                    "after": period.start_epoch,
                    "before": period.end_epoch,
                },
            )
            page_items = _map_external_data(
                map_activity_list,
                response,
                resource="activity list",
            )
            activities.extend(page_items)
            if len(page_items) < self._page_size:
                return activities
        raise InvalidExternalDataError(
            f"Strava activity pagination exceeded {self._max_pages} pages."
        )

    async def get_activity_details(self, activity_id: int) -> DetailedActivity:
        activity_id = require_activity_id(activity_id)
        response = await self._api.make_request(f"/activities/{activity_id}")
        activity = _map_external_data(map_activity, response, resource="activity")
        if activity.id != activity_id:
            raise InvalidExternalDataError(
                "Strava returned details for a different activity ID."
            )
        return activity

    async def get_activity_stream(self, activity_id: int) -> ActivityStream:
        activity_id = require_activity_id(activity_id)
        response = await self._api.make_request(
            f"/activities/{activity_id}/streams",
            {
                "keys": ",".join(STREAM_KEYS),
                "key_by_type": "true",
            },
        )
        try:
            return map_activity_stream(activity_id, response)
        except (TypeError, ValueError) as error:
            raise InvalidExternalDataError(
                "Strava returned invalid activity stream data."
            ) from error

    async def get_activity_zones(self, activity_id: int) -> HeartRateZones:
        activity_id = require_activity_id(activity_id)
        response = await self._api.make_request(f"/activities/{activity_id}/zones")
        try:
            return map_heart_rate_zones(activity_id, response)
        except (TypeError, ValueError) as error:
            raise InvalidExternalDataError(
                "Strava returned invalid heart-rate zone data."
            ) from error


def _map_external_data[T](
    mapper: Callable[[object], T],
    payload: object,
    *,
    resource: str,
) -> T:
    try:
        return mapper(payload)
    except (TypeError, ValueError) as error:
        raise InvalidExternalDataError(
            f"Strava returned invalid {resource} data."
        ) from error
