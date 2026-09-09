from collections.abc import Mapping, Sequence
from typing import ClassVar, cast

from src.core.ports.export import ActivityZonesWriter
from src.core.ports.strava import StravaAPI


class ActivityZones:
    ZONE_KEYS: ClassVar[tuple[str, ...]] = (
        "Zone_1",
        "Zone_2",
        "Zone_3",
        "Zone_4",
        "Zone_5",
    )

    def __init__(
        self,
        api: StravaAPI,
        activity_id: int | None,
        writer: ActivityZonesWriter | None = None,
    ) -> None:
        self._api = api
        self._activity_id = activity_id
        self._writer = writer

    async def get_zones(self, save_zones: bool = False) -> dict[str, object]:
        if not self._activity_id:
            raise ValueError("Activity ID is required for this operation.")

        response = await self._api.make_request(
            f"/activities/{self._activity_id}/zones"
        )
        if not isinstance(response, Mapping):
            raise TypeError("Strava zones response must be an object.")
        zones = response.get("distribution_buckets")
        if zones is None:
            raise ValueError("The activity does not have heartrate information.")
        if not isinstance(zones, Sequence) or isinstance(zones, (str, bytes)):
            raise TypeError("Strava zone buckets must be a sequence.")
        if len(zones) != len(self.ZONE_KEYS):
            raise ValueError("Strava must return exactly five heartrate zones.")

        zone_values = cast(Sequence[object], zones)
        zones_dict = dict(zip(self.ZONE_KEYS, zone_values, strict=True))
        if save_zones:
            if self._writer is None:
                raise RuntimeError("No activity zones writer has been configured.")
            self._writer.write(self._activity_id, zones_dict)

        return zones_dict
