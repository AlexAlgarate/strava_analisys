from src import strava_service
from src.access_token import GetAccessToken
from src.menu_handler import MenuHandler
from src.strava_api import (
    AsyncStravaAPI,
    SyncStravaAPI,
)
from src.utils import helpers as helper


def main():
    logger = helper.Logger().setup_logger()
    access_token = GetAccessToken(logger=logger).get_access_token()
    strava_API_sync = SyncStravaAPI(access_token=access_token)
    strava_API_async = AsyncStravaAPI(access_token=access_token)

    service = strava_service.StravaService(strava_API_sync, strava_API_async)
    menu = MenuHandler(service=service)

    while True:
        menu.print_menu()
        option = input("\nChoose an option (number or 'q' to exit): ")

        if option.lower() == "q":
            print("👋 Goodbye")
            break

        menu.execute_option(option)
    # while True:
    #     strava_service.print_(constant.PRINT_OPTIONS)
    #     choice = input("\nChoose an option (number or 'exit'): ")

    #     function_map = strava_service.get_function_map(
    #         api_sync=strava_API_sync, api_async=strava_API_async
    #     )
    #     if choice.lower() == constant.EXIT_OPTION:
    #         print("\nGoodbye!\n")
    #         break

    #     if choice not in constant.PRINT_OPTIONS:
    #         print("\nNot a valid option. Please, enter a number or 'exit'.")
    #         continue

    #     print(f"\nOption choosen --> {choice}. {constant.PRINT_OPTIONS[choice]}\n")
    #     action = function_map.get(choice)
    #     if action:
    #         try:
    #             action()

    #         except Exception as e:
    #             logger.error(f"Error executing option: {e}", exc_info=True)
    #     else:
    #         print("\nNot a valid option.")


if __name__ == "__main__":
    main()
