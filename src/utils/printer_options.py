import asyncio
from typing import Callable, Dict

from src.activities import (
    Activity,
    GetActivityDetails,
    GetActivityRange,
    GetLast200Activities,
    GetOneActivity,
)
from src.strava_api import InterfaceStravaAPI
from src.utils import constant


async def run_async_streams(access_token: str):
    result = await Activity.get_multiple_activities_streams(
        access_token,
        constant.EXAMPLE_ID_ACTIVITIES,
        constant.ACTIVITY_STREAMS_KEYS,
    )

    print(result)


async def run_async_activity_range(
    api: InterfaceStravaAPI, previous_week: bool = False
):
    result = await GetActivityRange(api=api).fetch_activity_data(
        previous_week=previous_week
    )
    print(result)


async def show_activity_details(api: InterfaceStravaAPI, previous_week: bool = False):
    result = await GetActivityDetails(api=api).fetch_activity_data(
        keys=constant.ACTIVITY_DETAILED_KEYS,
        previuos_week=previous_week,
    )
    print(result)


def show_one_activity(api: InterfaceStravaAPI):
    result = GetOneActivity(api=api, id_activity=13654451097).fetch_activity_data()
    print(result)


def show_last_200_activities(api: InterfaceStravaAPI):
    result = GetLast200Activities(api=api).fetch_activity_data()
    print(result)


def get_function_map(api, access_token: str) -> Dict[str, Callable]:
    return {
        "1": lambda: show_one_activity(api),
        "2": lambda: asyncio.run(show_activity_details(api, previous_week=False)),
        "3": lambda: asyncio.run(show_activity_details(api, previous_week=True)),
        "4": lambda: show_last_200_activities(api),
        "5": lambda: asyncio.run(run_async_activity_range(api, previous_week=False)),
        "6": lambda: asyncio.run(run_async_activity_range(api, previous_week=True)),
        "7": lambda: asyncio.run(run_async_streams(access_token)),
        "8": lambda: asyncio.run(run_async_streams(access_token)),
    }
