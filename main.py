import asyncio

from src import utils as utils
from src.access_token import GetAccessToken
from src.activities import ActivitiesManager


def run_async_streams(access_token: str):
    print(
        asyncio.run(
            ActivitiesManager.get_multiple_activities_streams(
                access_token,
                utils.id_activities,
                utils.streams_keys,
            )
        )
    )


def run_async_activity_range(access_token: str, previous_week: bool = False):
    print(
        asyncio.run(
            ActivitiesManager(access_token).get_activity_range_async(
                previous_week=previous_week
            )
        )
    )


def show_one_activity(access_token: str):
    print(ActivitiesManager(access_token).get_one_activity(13200148363))


def show_last_200_activities(access_token: str):
    print(ActivitiesManager(access_token).get_last_200_activities())


def print_options():
    print("\nChoose an option:")

    print("\nStrava - Options:")
    print("1. Show information for a specific activity")
    print("2. Show information for activities from the current week")
    print("3. Show the last 200 activities")
    print("4. Show information for activities from the previous week")
    print("5. Show streams for activities from the current week")
    print("6. Show a graph of time in zone for a specific activity")
    print("7. Show commit history")
    print("8. Exit")


def main():
    access_token = GetAccessToken().get_access_token()

    while True:
        print_options()
        choice = input("Choose an option: (1 to 8) ")

        match choice:
            case "1":
                show_one_activity(access_token)

            case "2":
                run_async_activity_range(access_token, previous_week=False)

            case "3":
                show_last_200_activities(access_token)

            case "4":
                run_async_activity_range(access_token, previous_week=True)

            case "5":
                run_async_streams(access_token)

            case "6":
                print("Feature not implemented yet.")

            case "7":
                print("Feature not implemented yet.")

            case "8":
                print("Goodbye!")
                break
            case _:
                print("Not valid option.")


if __name__ == "__main__":
    main()
