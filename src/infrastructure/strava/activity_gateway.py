from src.domain.activity_stream import ActivityStream
from src.domain.detailed_activity import DetailedActivity
from src.domain.heart_rate_zones import HeartRateZones
from src.domain.week_period import WeekPeriod
from src.infrastructure.api_clients.async_strava_api import AsyncStravaAPI
from src.infrastructure.strava.activity_mapper import map_activity, map_activity_list
from src.infrastructure.strava.heart_rate_zone_mapper import map_heart_rate_zones
from src.infrastructure.strava.stream_mapper import map_activity_stream

DEFAULT_PAGE_SIZE = 200
STREAM_KEYS = ("time", "distance", "heartrate")
ATHLETE_ACTIVITIES_ENDPOINT = "/athlete/activities"


class StravaActivityGateway:
    """Adapt Strava's HTTP API to the domain-oriented activity gateway."""

    def __init__(
        self,
        api: AsyncStravaAPI,
        *,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> None:
        if page_size < 1:
            raise ValueError("Activity page size must be at least one.")
        self._api = api
        self._page_size = page_size

    async def list_activities(self, period: WeekPeriod) -> list[DetailedActivity]:
        activities: list[DetailedActivity] = []
        page = 1
        while True:
            response = await self._api.make_request(
                endpoint=ATHLETE_ACTIVITIES_ENDPOINT,
                params={
                    "per_page": self._page_size,
                    "page": page,
                    "after": period.start_epoch,
                    "before": period.end_epoch,
                },
            )
            page_items = map_activity_list(response)
            activities.extend(page_items)
            if len(page_items) < self._page_size:
                return activities
            page += 1

    async def get_activity_details(self, activity_id: int) -> DetailedActivity:
        response = await self._api.make_request(f"/activities/{activity_id}")
        return map_activity(response)

    async def get_activity_stream(self, activity_id: int) -> ActivityStream:
        response = await self._api.make_request(
            f"/activities/{activity_id}/streams",
            {
                "keys": ",".join(STREAM_KEYS),
                "key_by_type": "true",
            },
        )
        return map_activity_stream(activity_id, response)

    async def get_activity_zones(self, activity_id: int) -> HeartRateZones:
        response = await self._api.make_request(f"/activities/{activity_id}/zones")
        return map_heart_rate_zones(activity_id, response)
