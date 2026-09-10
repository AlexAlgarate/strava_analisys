import asyncio
from typing import cast
from unittest.mock import patch

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
async def test_empty_input_returns_without_calling_operation() -> None:
    operation_called = False

    async def operation(value: int) -> int:
        nonlocal operation_called
        operation_called = True
        return value

    result = await map_concurrently([], operation)

    assert result == []
    assert not operation_called


@pytest.mark.asyncio
async def test_uses_a_bounded_number_of_worker_tasks() -> None:
    async def double(value: int) -> int:
        await asyncio.sleep(0)
        return value * 2

    loop = asyncio.get_running_loop()
    with patch.object(loop, "create_task", wraps=loop.create_task) as create_task:
        result = await map_concurrently(range(100), double, max_concurrency=3)

    assert result == [value * 2 for value in range(100)]
    assert create_task.call_count == 3


@pytest.mark.asyncio
async def test_cancels_and_awaits_sibling_workers_before_propagating_failure() -> None:
    expected_error = RuntimeError("operation failed")
    all_workers_started = asyncio.Event()
    never_complete = asyncio.Event()
    started: set[int] = set()
    cancelled: set[int] = set()

    async def fail_one_operation(value: int) -> int:
        started.add(value)
        if len(started) == 3:
            all_workers_started.set()
        await all_workers_started.wait()
        if value == 0:
            raise expected_error

        try:
            await never_complete.wait()
        except asyncio.CancelledError:
            cancelled.add(value)
            raise
        return value

    with pytest.raises(RuntimeError) as raised:
        await map_concurrently(range(10), fail_one_operation, max_concurrency=3)

    assert raised.value is expected_error
    assert started == {0, 1, 2}
    assert cancelled == {1, 2}


@pytest.mark.asyncio
@pytest.mark.parametrize("max_concurrency", [0, -1])
async def test_rejects_non_positive_concurrency_limit(max_concurrency: int) -> None:
    async def identity(value: int) -> int:
        return value

    with pytest.raises(ValueError, match="at least one"):
        await map_concurrently([1], identity, max_concurrency=max_concurrency)


@pytest.mark.asyncio
@pytest.mark.parametrize("max_concurrency", [True, 1.5])
async def test_rejects_non_integer_concurrency_limit(max_concurrency: object) -> None:
    async def identity(value: int) -> int:
        return value

    with pytest.raises(TypeError, match="must be an integer"):
        await map_concurrently(
            [1],
            identity,
            max_concurrency=cast(int, max_concurrency),
        )
