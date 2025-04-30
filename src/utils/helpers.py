import datetime
import time
from typing import Dict, List

import pandas as pd


def func_time_execution(func):
    async def wrapper(*args, **kwargs):
        start = time.time()
        result = await func(*args, **kwargs)
        end = time.time()
        print(f"\nExecution time: {end - start:.2f} seconds\n")
        return result

    return wrapper


def get_week_epoch_range(previous_week: bool = False) -> tuple[int, int]:
    today = datetime.datetime.today()
    _, _, iso_weekday = today.isocalendar()
    days_to_monday = 1 - iso_weekday

    if previous_week:
        days_to_monday -= 7

    start_of_week = today + datetime.timedelta(days=days_to_monday)
    end_of_week = start_of_week + datetime.timedelta(days=6)

    start_timestamp = int(
        start_of_week.replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
    )
    end_timestamp = int(
        end_of_week.replace(
            hour=23, minute=59, second=59, microsecond=999999
        ).timestamp()
    )

    return start_timestamp, end_timestamp


def process_streams(response: Dict, id_activity: int) -> pd.DataFrame:
    max_length = (
        max(
            len(stream_data.get("data", []))
            for stream_data in response.values()
            if isinstance(stream_data, dict)
        )
        if response
        else 0
    )

    data = {}
    for stream_type, stream_data in response.items():
        if isinstance(stream_data, dict) and "data" in stream_data:
            data[stream_type] = stream_data["data"]

            if len(data[stream_type]) < max_length:
                data[stream_type].extend([None] * (max_length - len(data[stream_type])))
        else:
            data[stream_type] = [None] * max_length

    df = pd.DataFrame(data)
    df["id"] = id_activity
    return df


async def get_activity_ids(activities: List[dict]) -> List[int]:
    return [activity["id"] for activity in activities]
