from src.access_token import GetAccessToken
from src.strava_api import (
    AsyncStravaAPI,
    SyncStravaAPI,
)
from src.utils import constants as constant
from src.utils import helpers as helper
from src.utils import printer_options as printer


def main():
    logger = helper.Logger().setup_logger()
    access_token = GetAccessToken(logger=logger).get_access_token()
    strava_API_sync = SyncStravaAPI(access_token=access_token)
    strava_API_async = AsyncStravaAPI(access_token=access_token)

    while True:
        printer.print_options(constant.PRINT_OPTIONS)
        choice = input("\nChoose an option (number or 'exit'): ")

        function_map = printer.get_function_map(
            api_sync=strava_API_sync, api_async=strava_API_async
        )
        if choice.lower() == constant.EXIT_OPTION:
            print("\nGoodbye!\n")
            break

        if choice not in constant.PRINT_OPTIONS:
            print("\nNot a valid option. Please, enter a number or 'exit'.")
            continue

        print(f"\nOption choosen --> {choice}. {constant.PRINT_OPTIONS[choice]}\n")
        action = function_map.get(choice)
        if action:
            try:
                action()

            except Exception as e:
                logger.error(f"Error executing option: {e}", exc_info=True)
        else:
            print("\nNot a valid option.")


if __name__ == "__main__":
    main()
