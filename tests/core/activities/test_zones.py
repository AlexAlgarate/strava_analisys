import json
import os
from tempfile import TemporaryDirectory
from unittest.mock import AsyncMock, Mock

import pytest

from src.core.activities.zones import ActivityZones


@pytest.fixture
def mock_async_api():
    api = Mock()
    api.make_request = AsyncMock()
    return api


@pytest.fixture
def zones_manager(mock_async_api):
    return ActivityZones(api=mock_async_api, id_activity=123)


class TestActivityZones:
    @pytest.mark.asyncio
    async def test_get_zones_success(self, zones_manager, mock_async_api):
        mock_response = {"distribution_buckets": [10, 20, 30, 40, 50]}
        mock_async_api.make_request.return_value = mock_response

        result = await zones_manager.get_zones()

        assert isinstance(result, dict)
        assert len(result) == 5
        assert all(f"Zone_{i}" in result for i in range(1, 6))
        assert list(result.values()) == [10, 20, 30, 40, 50]

    @pytest.mark.asyncio
    async def test_get_zones_no_id(self, mock_async_api):
        zones_manager = ActivityZones(api=mock_async_api, id_activity=None)
        with pytest.raises(ValueError, match="Activity ID is required"):
            await zones_manager.get_zones()

    @pytest.mark.asyncio
    async def test_get_zones_no_heartrate(self, zones_manager, mock_async_api):
        mock_response = {"distribution_buckets": None}
        mock_async_api.make_request.return_value = mock_response

        with pytest.raises(ValueError, match="does not have heartrate information"):
            await zones_manager.get_zones()

    @pytest.mark.asyncio
    async def test_get_zones_with_save(self, zones_manager, mock_async_api):
        mock_response = {"distribution_buckets": [10, 20, 30, 40, 50]}
        mock_async_api.make_request.return_value = mock_response

        with TemporaryDirectory() as tmp_dir:
            # Change working directory temporarily
            original_dir = os.getcwd()
            os.chdir(tmp_dir)

            try:
                result = await zones_manager.get_zones(save_zones=True)

                # Verify the file was created
                file_path = "json_zones_files/zones_123.json"
                assert os.path.exists(file_path)

                # Verify file contents
                with open(file_path) as f:
                    saved_data = json.load(f)
                    assert saved_data == result

            finally:
                # Restore original working directory
                os.chdir(original_dir)
