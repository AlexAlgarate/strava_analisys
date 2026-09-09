import functools
import os
import time
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime, timedelta


def func_time_execution[**P, R](
    func: Callable[P, Awaitable[R]],
) -> Callable[P, Awaitable[R]]:
    """Decorator to measure function execution time."""

    @functools.wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        start_time = time.perf_counter()
        result = await func(*args, **kwargs)
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        function_name = getattr(func, "__name__", func.__class__.__name__)
        print(f"{function_name} took {execution_time:.2f} seconds to execute.")
        return result

    return wrapper


def check_path(path: str) -> bool:
    """Check if a path exists."""
    return os.path.exists(path)


def get_week_epoch_range(previous_week: bool = False) -> tuple[int, int]:
    """Get epoch timestamp range for current or previous week."""
    now = datetime.now(UTC)
    current_weekday = now.weekday()
    monday = now - timedelta(days=current_weekday)

    if previous_week:
        monday = monday - timedelta(weeks=1)

    # Reset to start of Monday (00:00:00)
    monday = monday.replace(hour=0, minute=0, second=0, microsecond=0)
    sunday = monday + timedelta(days=7)

    return int(monday.timestamp()), int(sunday.timestamp())
