import functools
import os
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Tuple


def func_time_execution(func: Callable) -> Callable:
    """Decorator to measure function execution time."""

    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.perf_counter()
        result = await func(*args, **kwargs)
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        print(f"{func.__name__} took {execution_time:.2f} seconds to execute.")
        return result

    return wrapper


def check_path(path: str) -> bool:
    """Check if a path exists."""
    return os.path.exists(path)


def get_week_epoch_range(previous_week: bool = False) -> Tuple[int, int]:
    """Get epoch timestamp range for current or previous week."""
    now = datetime.now(timezone.utc)
    current_weekday = now.weekday()
    monday = now - timedelta(days=current_weekday)

    if previous_week:
        monday = monday - timedelta(weeks=1)

    # Reset to start of Monday (00:00:00)
    monday = monday.replace(hour=0, minute=0, second=0, microsecond=0)
    sunday = monday + timedelta(days=7)

    return int(monday.timestamp()), int(sunday.timestamp())
