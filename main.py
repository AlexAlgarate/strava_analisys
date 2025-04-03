from src import strava_service
from src.access_token import GetAccessToken
from src.menu.handler import MenuHandler
from src.menu.options import MenuOption
from src.strava_api.api_requests.async_request import AsyncStravaAPI
from src.strava_api.api_requests.sync_request import SyncStravaAPI
from src.utils.logging import Logger


def main():
    logger = Logger().setup_logger()
    access_token = GetAccessToken(logger=logger).get_access_token()
    strava_API_sync = SyncStravaAPI(access_token=access_token)
    strava_API_async = AsyncStravaAPI(access_token=access_token)

    service = strava_service.StravaService(strava_API_sync, strava_API_async)
    menu = MenuHandler(service=service)

    while True:
        menu.print_menu(menu_option=MenuOption)
        option = input("\nChoose an option (number or 'q' to exit): ")

        if option.lower() == "q":
            print("👋 Goodbye")
            break

        menu.execute_option(option)


if __name__ == "__main__":
    main()
