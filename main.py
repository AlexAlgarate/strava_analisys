import asyncio
from typing import Dict

from src.access_token import GetAccessToken
from src.activities import (
    Activity,
    GetActivityDetails,
    GetActivityRange,
    GetLast200Activities,
    GetOneActivity,
)
from src.strava_api import InterfaceStravaAPI, StravaAPI
from src.utils import constants as constant


def run_async_streams(access_token: str):
    print(
        asyncio.run(
            Activity.get_multiple_activities_streams(
                access_token,
                constant.EXAMPLE_ID_ACTIVITIES,
                constant.ACTIVITY_STREAMS_KEYS,
            )
        )
    )


def run_async_activity_range(api: InterfaceStravaAPI, previous_week: bool = False):
    print(
        asyncio.run(
            GetActivityRange(api=api).fetch_activity_data(previous_week=previous_week)
        )
    )


def show_activity_details(api: InterfaceStravaAPI, previous_week: bool = False):
    print(
        asyncio.run(
            GetActivityDetails(api=api).fetch_activity_data(
                keys=constant.ACTIVITY_DETAILED_KEYS,
                previuos_week=previous_week,
            )
        )
    )


def show_one_activity(api: InterfaceStravaAPI):
    print(GetOneActivity(api=api, id_activity=13654451097).fetch_activity_data())


def show_last_200_activities(api: InterfaceStravaAPI):
    print(GetLast200Activities(api=api).fetch_activity_data())


def print_options(options: Dict[str, str]) -> None:
    print("\nChoose an option:")

    for key, value in options.items():
        print(f"{key}. {value}")


def main():
    access_token = GetAccessToken().get_access_token()
    Strava_API = StravaAPI(access_token=access_token)
    while True:
        print_options(constant.print_options_main)
        choice = input(f"Choose an option: (1 to {len(constant.print_options_main)}) ")

        match choice:
            case "1":
                show_one_activity(api=Strava_API)

            case "2":
                show_activity_details(api=Strava_API, previous_week=True)

            case "3":
                show_last_200_activities(api=Strava_API)

            case "4":
                run_async_activity_range(api=Strava_API, previous_week=False)

            case "5":
                run_async_activity_range(api=Strava_API, previous_week=True)

            case "6":
                run_async_streams(access_token)

            case "7":
                print("Feature not implemented yet.")

            case "8":
                print("\nGoodbye!")
                break
            case _:
                print("Not valid option.")


if __name__ == "__main__":
    main()
