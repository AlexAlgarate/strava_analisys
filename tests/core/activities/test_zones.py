import json
from pathlib import Path
from typing import cast
from unittest.mock import AsyncMock, Mock

import pytest

from src.core.activities.zones import ActivityZones
from src.domain.heart_rate_zones import HeartRateZones
from src.infrastructure.export.json_activity_zones_writer import (
    JsonActivityZonesWriter,
)
from tests.factories import zones_payload


@pytest.fixture
def mock_async_api() -> Mock:
    api = Mock()
    api.make_request = AsyncMock()
    return api


@pytest.fixture
def zones_manager(mock_async_api: Mock) -> ActivityZones:
    return ActivityZones(api=mock_async_api, activity_id=123)


@pytest.mark.asyncio
async def test_get_zones_returns_domain_model(
    zones_manager: ActivityZones,
    mock_async_api: Mock,
) -> None:
    mock_async_api.make_request.return_value = zones_payload()

    result = await zones_manager.get_zones()

    assert isinstance(result, HeartRateZones)
    assert result.activity_id == 123
    assert len(result.zones) == 5
    assert result.zones[0].time_seconds == 300


@pytest.mark.asyncio
async def test_accepts_strava_zone_list_response(
    zones_manager: ActivityZones,
    mock_async_api: Mock,
) -> None:
    mock_async_api.make_request.return_value = [
        {"type": "power", "distribution_buckets": []},
        {"type": "heartrate", **zones_payload()},
    ]

    result = await zones_manager.get_zones()

    assert len(result.zones) == 5


@pytest.mark.asyncio
async def test_get_zones_requires_activity_id(mock_async_api: Mock) -> None:
    with pytest.raises(ValueError, match="Activity ID is required"):
        await ActivityZones(api=mock_async_api, activity_id=None).get_zones()


@pytest.mark.parametrize("activity_id", [True, 0])
def test_rejects_invalid_activity_id(
    mock_async_api: Mock,
    activity_id: object,
) -> None:
    expected_error = TypeError if activity_id is True else ValueError
    with pytest.raises(expected_error):
        ActivityZones(api=mock_async_api, activity_id=cast(int, activity_id))


@pytest.mark.asyncio
async def test_get_zones_rejects_missing_heartrate_data(
    zones_manager: ActivityZones,
    mock_async_api: Mock,
) -> None:
    mock_async_api.make_request.return_value = {"distribution_buckets": None}

    with pytest.raises(ValueError, match="does not have heartrate information"):
        await zones_manager.get_zones()


@pytest.mark.asyncio
async def test_get_zones_rejects_invalid_response_shape(
    zones_manager: ActivityZones,
    mock_async_api: Mock,
) -> None:
    mock_async_api.make_request.return_value = "invalid"

    with pytest.raises(TypeError, match="object or a sequence"):
        await zones_manager.get_zones()


@pytest.mark.asyncio
async def test_get_zones_rejects_wrong_number_of_buckets(
    zones_manager: ActivityZones,
    mock_async_api: Mock,
) -> None:
    mock_async_api.make_request.return_value = {"distribution_buckets": []}

    with pytest.raises(ValueError, match="exactly five"):
        await zones_manager.get_zones()


@pytest.mark.asyncio
async def test_save_requires_writer(
    zones_manager: ActivityZones,
    mock_async_api: Mock,
) -> None:
    mock_async_api.make_request.return_value = zones_payload()

    with pytest.raises(RuntimeError, match="writer has been configured"):
        await zones_manager.get_zones(save_zones=True)


@pytest.mark.asyncio
async def test_get_zones_with_save(
    tmp_path: Path,
    mock_async_api: Mock,
) -> None:
    mock_async_api.make_request.return_value = zones_payload()
    zones_manager = ActivityZones(
        api=mock_async_api,
        activity_id=123,
        writer=JsonActivityZonesWriter(tmp_path),
    )

    await zones_manager.get_zones(save_zones=True)

    with (tmp_path / "zones_123.json").open(encoding="utf-8") as source:
        assert json.load(source) == {
            "Zone_1": {"min": 0, "max": 120, "time": 300},
            "Zone_2": {"min": 120, "max": 140, "time": 600},
            "Zone_3": {"min": 140, "max": 160, "time": 900},
            "Zone_4": {"min": 160, "max": 180, "time": 400},
            "Zone_5": {"min": 180, "max": -1, "time": 120},
        }
