import asyncio

import pytest

from src.application.concurrency import map_concurrently


@pytest.mark.asyncio
async def test_maps_concurrently_while_preserving_input_order() -> None:
    active = 0
    peak = 0

    async def double(value: int) -> int:
        nonlocal active, peak
        active += 1
        peak = max(peak, active)
        await asyncio.sleep(0)
        active -= 1
        return value * 2

    result = await map_concurrently([3, 1, 2], double, max_concurrency=2)

    assert result == [6, 2, 4]
    assert peak == 2


@pytest.mark.asyncio
async def test_rejects_invalid_concurrency_limit() -> None:
    async def identity(value: int) -> int:
        return value

    with pytest.raises(ValueError, match="at least one"):
        await map_concurrently([1], identity, max_concurrency=0)
