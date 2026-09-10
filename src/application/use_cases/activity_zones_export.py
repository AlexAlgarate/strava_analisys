from src.application.ports.export import ActivityZonesWriter
from src.application.ports.use_cases import ActivityZonesUseCase
from src.application.results import ActivityZonesExportResult


class ActivityZonesExportService:
    """Retrieve and persist heart-rate zones for one activity."""

    def __init__(
        self,
        activity_zones: ActivityZonesUseCase,
        writer: ActivityZonesWriter,
    ) -> None:
        self._activity_zones = activity_zones
        self._writer = writer

    async def export_activity_zones(
        self,
        activity_id: int,
    ) -> ActivityZonesExportResult:
        zones = await self._activity_zones.get_activity_zones(activity_id)
        path = self._writer.write(zones)
        return ActivityZonesExportResult(zones=zones, path=path)
