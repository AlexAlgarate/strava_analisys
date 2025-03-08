import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict

import pandas as pd


class Logger:
    @staticmethod
    def setup_logger():
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        return logging.getLogger(__name__)


def func_time_execution(func):
    async def wraper(*args, **kwargs):
        start = time.time()
        result = await func(*args, **kwargs)
        end = time.time()
        print(f"\nExecution time: {end - start:.2f} seconds\n")
        return result

    return wraper


def get_epoch_times_for_week(previous_week: bool = False) -> tuple:
    today = datetime.today()
    _iso_year, _iso_week, iso_weekday = today.isocalendar()
    days_offset = -iso_weekday + 1 - (7 if previous_week else 0)

    start_of_week = today + timedelta(days=days_offset)
    end_of_week = start_of_week + timedelta(days=6)

    start_of_week_epoch = int(
        start_of_week.replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
    )
    end_of_week_epoch = int(
        end_of_week.replace(
            hour=23, minute=59, second=59, microsecond=999999
        ).timestamp()
    )

    return start_of_week_epoch, end_of_week_epoch


def check_path(target_path: str) -> bool:
    execution_path = Path(__file__).parent
    target_directory = execution_path / target_path
    if not target_directory.exists():
        target_directory.mkdir(parents=True, exist_ok=True)
    return target_directory.is_dir()


def process_streams(response: Dict, id_activity: int) -> pd.DataFrame:
    """Transform API response into a structured DataFrame."""
    data = {
        stream_type: stream_data.get("data", [])
        for stream_type, stream_data in response.items()
    }
    df = pd.DataFrame(data)
    df["id"] = id_activity
    return df
