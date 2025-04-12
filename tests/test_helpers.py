import asyncio
from datetime import datetime

import pandas as pd
import pytest
from freezegun import freeze_time

from src.utils.helpers import (
    check_path,
    func_time_execution,
    get_epoch_times_for_week,
    process_streams,
)


class TestEpochTimeCalculation:
    @freeze_time("2025-04-14")  # A Monday
    def test_get_epoch_times_current_week(self):
        # Freeze time to a Monday for consistent testing

        start, end = get_epoch_times_for_week(previous_week=False)

        # Start should be Monday 00:00:00
        assert (
            datetime.fromtimestamp(start).strftime("%Y-%m-%d %H:%M:%S")
            == "2025-04-14 00:00:00"
        )
        # End should be Sunday 23:59:59
        assert (
            datetime.fromtimestamp(end).strftime("%Y-%m-%d %H:%M:%S")
            == "2025-04-20 23:59:59"
        )

    @freeze_time("2025-04-14")  # A Monday
    def test_get_epoch_times_previous_week(self):
        start, end = get_epoch_times_for_week(previous_week=True)

        # Should be previous week
        assert (
            datetime.fromtimestamp(start).strftime("%Y-%m-%d %H:%M:%S")
            == "2025-04-07 00:00:00"
        )
        assert (
            datetime.fromtimestamp(end).strftime("%Y-%m-%d %H:%M:%S")
            == "2025-04-13 23:59:59"
        )


class TestPathHelper:
    def test_check_path_existing_directory(self, tmp_path):
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()

        with pytest.MonkeyPatch.context() as mp:
            mp.chdir(tmp_path)
            assert check_path(str(test_dir)) is True

    def test_check_path_create_directory(self, tmp_path):
        test_dir = tmp_path / "new_test_dir"

        with pytest.MonkeyPatch.context() as mp:
            mp.chdir(tmp_path)
            assert check_path(str(test_dir)) is True
            assert test_dir.is_dir()


class TestStreamProcessing:
    def test_process_streams_basic(self):
        test_data = {
            "time": {"data": [0, 1, 2]},
            "distance": {"data": [0, 100, 200]},
            "heartrate": {"data": [60, 65, 70]},
        }

        result = process_streams(test_data, id_activity=123)

        assert isinstance(result, pd.DataFrame)
        assert list(result.columns) == ["time", "distance", "heartrate", "id"]
        assert len(result) == 3
        assert all(result["id"] == 123)

    def test_process_streams_empty_data(self):
        test_data = {
            "time": {"data": []},
            "distance": {"data": []},
            "heartrate": {"data": []},
        }

        result = process_streams(test_data, id_activity=123)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
        assert "id" in result.columns

    def test_process_streams_missing_data(self):
        test_data = {
            "time": {"data": [0, 1]},
            "distance": {},  # Missing data
            "heartrate": {"data": [60, 65]},
        }

        result = process_streams(test_data, id_activity=123)

        assert isinstance(result, pd.DataFrame)
        assert list(result.columns) == ["time", "distance", "heartrate", "id"]
        assert len(result) == 2
        assert all(result["distance"].isna())  # Distance column should be NaN


@pytest.mark.asyncio
async def test_func_time_execution_decorator():
    @func_time_execution
    async def mock_async_function():
        await asyncio.sleep(0.1)
        return "test result"

    result = await mock_async_function()

    assert result == "test result"
