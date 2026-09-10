from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest

from src.application.ports.export import ActivityZonesWriter
from src.application.ports.use_cases import ActivityZonesUseCase
from src.application.use_cases.activity_zones_export import (
    ActivityZonesExportService,
)
from tests.factories import heart_rate_zones


@pytest.mark.asyncio
async def test_exports_zones_retrieved_for_activity(tmp_path: Path) -> None:
    zones = heart_rate_zones(123)
    activity_zones = Mock(spec=ActivityZonesUseCase)
    activity_zones.get_activity_zones = AsyncMock(return_value=zones)
    path = tmp_path / "zones_123.json"
    writer = Mock(spec=ActivityZonesWriter)
    writer.write.return_value = path
    service = ActivityZonesExportService(activity_zones, writer)

    result = await service.export_activity_zones(123)

    assert result.zones is zones
    assert result.path == path
    activity_zones.get_activity_zones.assert_awaited_once_with(123)
    writer.write.assert_called_once_with(zones)


@pytest.mark.asyncio
async def test_does_not_write_when_retrieving_zones_fails() -> None:
    activity_zones = Mock(spec=ActivityZonesUseCase)
    activity_zones.get_activity_zones = AsyncMock(side_effect=TimeoutError("timed out"))
    writer = Mock(spec=ActivityZonesWriter)
    service = ActivityZonesExportService(activity_zones, writer)

    with pytest.raises(TimeoutError, match="timed out"):
        await service.export_activity_zones(123)

    writer.write.assert_not_called()


@pytest.mark.asyncio
async def test_propagates_writer_failure_after_retrieving_zones() -> None:
    zones = heart_rate_zones(123)
    activity_zones = Mock(spec=ActivityZonesUseCase)
    activity_zones.get_activity_zones = AsyncMock(return_value=zones)
    writer = Mock(spec=ActivityZonesWriter)
    writer.write.side_effect = OSError("disk full")
    service = ActivityZonesExportService(activity_zones, writer)

    with pytest.raises(OSError, match="disk full"):
        await service.export_activity_zones(123)

    activity_zones.get_activity_zones.assert_awaited_once_with(123)
    writer.write.assert_called_once_with(zones)
