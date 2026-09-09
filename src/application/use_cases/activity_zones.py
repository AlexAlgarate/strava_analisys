from src.application.ports.activity_gateway import ActivityGateway
from src.application.ports.export import ActivityZonesWriter
from src.domain.activity_id import require_activity_id
from src.domain.heart_rate_zones import HeartRateZones


class ActivityZonesService:
    """Retrieve heart-rate zones and optionally persist them."""

    def __init__(
        self,
        gateway: ActivityGateway,
        writer: ActivityZonesWriter | None = None,
    ) -> None:
        self._gateway = gateway
        self._writer = writer

    async def get_activity_zones(
        self,
        activity_id: int,
        save_zones: bool = False,
    ) -> HeartRateZones:
        zones = await self._gateway.get_activity_zones(
            require_activity_id(activity_id)
        )
        if save_zones:
            if self._writer is None:
                raise RuntimeError("No activity zones writer has been configured.")
            self._writer.write(zones)
        return zones
