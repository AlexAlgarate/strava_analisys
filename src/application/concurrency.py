import asyncio
from collections.abc import Awaitable, Callable, Sequence

DEFAULT_MAX_CONCURRENCY = 5


async def map_concurrently[T, R](
    items: Sequence[T],
    operation: Callable[[T], Awaitable[R]],
    *,
    max_concurrency: int = DEFAULT_MAX_CONCURRENCY,
) -> list[R]:
    """Apply an operation in input order using a bounded async worker pool.

    If one operation fails, pending workers are cancelled and awaited before the
    original exception is propagated.
    """
    max_concurrency = require_concurrency_limit(max_concurrency)

    item_count = len(items)
    if item_count == 0:
        return []

    results: dict[int, R] = {}
    next_index = 0

    async def worker() -> None:
        nonlocal next_index
        while next_index < item_count:
            index = next_index
            next_index += 1
            results[index] = await operation(items[index])

    workers = [
        asyncio.create_task(worker()) for _ in range(min(max_concurrency, item_count))
    ]
    try:
        await asyncio.gather(*workers)
    finally:
        for worker_task in workers:
            if not worker_task.done():
                worker_task.cancel()
        await asyncio.gather(*workers, return_exceptions=True)

    return [results[index] for index in range(item_count)]


def require_concurrency_limit(value: object) -> int:
    """Return a valid positive worker limit or raise a configuration error."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError("Maximum concurrency must be an integer.")
    if value < 1:
        raise ValueError("Maximum concurrency must be at least one.")
    return value
