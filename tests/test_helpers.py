import asyncio

import pytest
from freezegun import freeze_time

from src.utils.helpers import func_time_execution, get_week_epoch_range


class TestEpochTimeCalculation:
    def test_get_epoch_time_beginning_of_week(self) -> None:
        # Sunday
        with freeze_time("2024-01-21"):
            monday, sunday = get_week_epoch_range()
            assert isinstance(monday, int)
            assert isinstance(sunday, int)
            assert monday < sunday

    def test_get_epoch_time_middle_of_week(self) -> None:
        # Wednesday
        with freeze_time("2024-01-24"):
            monday, sunday = get_week_epoch_range()
            assert isinstance(monday, int)
            assert isinstance(sunday, int)
            assert monday < sunday

    def test_get_epoch_time_end_of_week(self) -> None:
        # Saturday
        with freeze_time("2024-01-27"):
            monday, sunday = get_week_epoch_range()
            assert isinstance(monday, int)
            assert isinstance(sunday, int)
            assert monday < sunday

    def test_get_epoch_time_previous_week(self) -> None:
        # Current week
        with freeze_time("2024-01-24"):
            current_monday, _ = get_week_epoch_range()
            previous_monday, _ = get_week_epoch_range(previous_week=True)

            assert previous_monday < current_monday
            assert (
                current_monday - previous_monday
            ) == 7 * 24 * 60 * 60  # One week difference


@pytest.mark.asyncio
async def test_func_time_execution_decorator() -> None:
    @func_time_execution
    async def sample_async_function() -> str:
        await asyncio.sleep(0.1)
        return "test"

    result = await sample_async_function()
    assert result == "test"
