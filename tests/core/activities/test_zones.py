import json
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest

from src.core.activities.zones import ActivityZones
from src.infrastructure.export.json_activity_zones_writer import (
    JsonActivityZonesWriter,
)


@pytest.fixture
def mock_async_api() -> Mock:
    api = Mock()
    api.make_request = AsyncMock()
    return api


@pytest.fixture
def zones_manager(mock_async_api: Mock) -> ActivityZones:
    return ActivityZones(api=mock_async_api, activity_id=123)


class TestActivityZones:
    @pytest.mark.asyncio
    async def test_get_zones_success(
        self, zones_manager: ActivityZones, mock_async_api: Mock
    ) -> None:
        mock_response = {"distribution_buckets": [10, 20, 30, 40, 50]}
        mock_async_api.make_request.return_value = mock_response

        result = await zones_manager.get_zones()

        assert isinstance(result, dict)
        assert len(result) == 5
        assert all(f"Zone_{i}" in result for i in range(1, 6))
        assert list(result.values()) == [10, 20, 30, 40, 50]

    @pytest.mark.asyncio
    async def test_get_zones_no_id(self, mock_async_api: Mock) -> None:
        zones_manager = ActivityZones(api=mock_async_api, activity_id=None)
        with pytest.raises(ValueError, match="Activity ID is required"):
            await zones_manager.get_zones()

    @pytest.mark.asyncio
    async def test_get_zones_no_heartrate(
        self, zones_manager: ActivityZones, mock_async_api: Mock
    ) -> None:
        mock_response = {"distribution_buckets": None}
        mock_async_api.make_request.return_value = mock_response

        with pytest.raises(ValueError, match="does not have heartrate information"):
            await zones_manager.get_zones()

    @pytest.mark.asyncio
    async def test_rejects_non_object_response(
        self, zones_manager: ActivityZones, mock_async_api: Mock
    ) -> None:
        mock_async_api.make_request.return_value = []

        with pytest.raises(TypeError, match="response must be an object"):
            await zones_manager.get_zones()

    @pytest.mark.asyncio
    async def test_rejects_non_sequence_buckets(
        self, zones_manager: ActivityZones, mock_async_api: Mock
    ) -> None:
        mock_async_api.make_request.return_value = {"distribution_buckets": "invalid"}

        with pytest.raises(TypeError, match="buckets must be a sequence"):
            await zones_manager.get_zones()

    @pytest.mark.asyncio
    async def test_rejects_wrong_number_of_buckets(
        self, zones_manager: ActivityZones, mock_async_api: Mock
    ) -> None:
        mock_async_api.make_request.return_value = {"distribution_buckets": [1, 2]}

        with pytest.raises(ValueError, match="exactly five"):
            await zones_manager.get_zones()

    @pytest.mark.asyncio
    async def test_save_requires_writer(
        self, zones_manager: ActivityZones, mock_async_api: Mock
    ) -> None:
        mock_async_api.make_request.return_value = {
            "distribution_buckets": [1, 2, 3, 4, 5]
        }

        with pytest.raises(RuntimeError, match="writer has been configured"):
            await zones_manager.get_zones(save_zones=True)

    @pytest.mark.asyncio
    async def test_get_zones_with_save(
        self, tmp_path: Path, mock_async_api: Mock
    ) -> None:
        mock_response = {"distribution_buckets": [10, 20, 30, 40, 50]}
        mock_async_api.make_request.return_value = mock_response
        zones_manager = ActivityZones(
            api=mock_async_api,
            activity_id=123,
            writer=JsonActivityZonesWriter(tmp_path),
        )

        result = await zones_manager.get_zones(save_zones=True)

        with (tmp_path / "zones_123.json").open() as source:
            assert json.load(source) == result
