from src.application.ports.activity_gateway import ActivityGateway
from src.domain.activity_id import require_activity_id
from src.domain.heart_rate_zones import HeartRateZones


class ActivityZonesService:
    """Retrieve heart-rate zones for one activity."""

    def __init__(self, gateway: ActivityGateway) -> None:
        self._gateway = gateway

    async def get_activity_zones(
        self,
        activity_id: int,
    ) -> HeartRateZones:
        return await self._gateway.get_activity_zones(require_activity_id(activity_id))
