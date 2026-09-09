from src.core.ports.export import ActivityZonesWriter
from src.core.ports.strava import StravaAPI
from src.domain.heart_rate_zones import HeartRateZones
from src.infrastructure.strava.heart_rate_zone_mapper import map_heart_rate_zones


class ActivityZones:
    def __init__(
        self,
        api: StravaAPI,
        activity_id: int | None,
        writer: ActivityZonesWriter | None = None,
    ) -> None:
        if activity_id is not None:
            if isinstance(activity_id, bool) or not isinstance(activity_id, int):
                raise TypeError("Activity ID must be an integer.")
            if activity_id <= 0:
                raise ValueError("Activity ID must be a positive integer.")
        self._api = api
        self._activity_id = activity_id
        self._writer = writer

    async def get_zones(self, save_zones: bool = False) -> HeartRateZones:
        if self._activity_id is None:
            raise ValueError("Activity ID is required for this operation.")

        response = await self._api.make_request(
            f"/activities/{self._activity_id}/zones"
        )
        zones = map_heart_rate_zones(self._activity_id, response)
        if save_zones:
            if self._writer is None:
                raise RuntimeError("No activity zones writer has been configured.")
            self._writer.write(zones)

        return zones
