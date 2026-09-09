import asyncio
from collections.abc import Awaitable, Callable, Sequence

DEFAULT_MAX_CONCURRENCY = 5


async def map_concurrently[T, R](
    items: Sequence[T],
    operation: Callable[[T], Awaitable[R]],
    *,
    max_concurrency: int = DEFAULT_MAX_CONCURRENCY,
) -> list[R]:
    """Apply an async operation in input order with bounded concurrency."""
    if max_concurrency < 1:
        raise ValueError("Maximum concurrency must be at least one.")

    semaphore = asyncio.Semaphore(max_concurrency)

    async def run(item: T) -> R:
        async with semaphore:
            return await operation(item)

    return list(await asyncio.gather(*(run(item) for item in items)))
