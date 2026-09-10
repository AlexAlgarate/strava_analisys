from unittest.mock import AsyncMock, Mock

import pytest

from src.application.ports.activity_gateway import ActivityZonesGateway
from src.application.use_cases.activity_zones import ActivityZonesService
from tests.factories import heart_rate_zones


@pytest.fixture
def gateway() -> Mock:
    result = Mock(spec=ActivityZonesGateway)
    result.get_activity_zones = AsyncMock(return_value=heart_rate_zones(123))
    return result


@pytest.mark.asyncio
async def test_returns_zones_from_gateway(gateway: Mock) -> None:
    service = ActivityZonesService(gateway)

    result = await service.get_activity_zones(123)

    assert result == heart_rate_zones(123)
    gateway.get_activity_zones.assert_awaited_once_with(123)


@pytest.mark.asyncio
async def test_rejects_invalid_id_before_calling_gateway(gateway: Mock) -> None:
    service = ActivityZonesService(gateway)

    with pytest.raises(ValueError, match="positive integer"):
        await service.get_activity_zones(0)

    gateway.get_activity_zones.assert_not_awaited()
