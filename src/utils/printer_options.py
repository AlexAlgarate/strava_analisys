import asyncio
from typing import Callable, Dict

from src.activities import (
    GetActivityDetails,
    GetActivityRange,
    GetLast200Activities,
    GetOneActivity,
    GetStreamsActivities,
)
from src.strava_api import AsyncStravaAPI, SyncStravaAPI
from src.utils import constants as constant


async def run_async_streams(api: AsyncStravaAPI):
    result = await GetStreamsActivities(
        api=api, id_activity=constant.EXAMPLE_ID_ACTIVITIES[0]
    ).fetch_activity_data(
        stream_keys=constant.ACTIVITY_STREAMS_KEYS,
    )

    print(result)


# async def run_async_streams(api: AsyncStravaAPI):
#     result = await GetStreamsActivities(api=api).fetch_activity_data(
#         list_id_activities=constant.EXAMPLE_ID_ACTIVITIES,
#         stream_keys=constant.ACTIVITY_STREAMS_KEYS,
#     )

#     print(result)


# async def run_async_streams(access_token: str):
#     result = await Activity.get_multiple_activities_streams(
#         access_token=access_token,
#         list_id_activities=constant.EXAMPLE_ID_ACTIVITIES,
#         stream_keys=constant.ACTIVITY_STREAMS_KEYS,
#     )

#     print(result)


async def run_async_activity_range(api: AsyncStravaAPI, previous_week: bool = False):
    result = await GetActivityRange(api=api).fetch_activity_data(
        previous_week=previous_week
    )
    print(result)


async def show_activity_details(api: AsyncStravaAPI, previous_week: bool = False):
    result = await GetActivityDetails(api=api).fetch_activity_data(
        keys=constant.ACTIVITY_DETAILED_KEYS,
        previuos_week=previous_week,
    )
    print(result)


def show_one_activity(api: SyncStravaAPI):
    result = GetOneActivity(api=api, id_activity=13654451097).fetch_activity_data()
    print(result)


def show_last_200_activities(api: SyncStravaAPI):
    result = GetLast200Activities(api=api).fetch_activity_data()
    print(result)


def get_function_map(
    api_sync: SyncStravaAPI, api_async: AsyncStravaAPI
) -> Dict[str, Callable]:
    return {
        "1": lambda: show_one_activity(api_sync),
        "2": lambda: asyncio.run(
            show_activity_details(
                api_async,
                previous_week=False,
            )
        ),
        "3": lambda: asyncio.run(
            show_activity_details(
                api_async,
                previous_week=True,
            )
        ),
        "4": lambda: show_last_200_activities(api_sync),
        "5": lambda: asyncio.run(
            run_async_activity_range(
                api_async,
                previous_week=False,
            )
        ),
        "6": lambda: asyncio.run(
            run_async_activity_range(
                api_async,
                previous_week=True,
            )
        ),
        "7": lambda: asyncio.run(run_async_streams(api_async)),
        # "8": lambda: asyncio.run(run_async_streams(api)),
    }


def print_options(options: Dict[str, str]) -> None:
    print("\nChoose an option:")

    for key, value in options.items():
        print(f"{key}. {value}")
