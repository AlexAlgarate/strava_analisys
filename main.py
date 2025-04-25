import logging

from src import strava_service
from src.access_token import GetAccessToken
from src.menu.console_error_handler import ConsoleErrorHandler
from src.menu.handler import MenuHandler
from src.menu.result_console_printer import ResultConsolePrinter
from src.strava_api.api.async_strava_api import AsyncStravaAPI
from src.strava_api.api.sync_strava_api import SyncStravaAPI
from src.utils.logger_config import setup_logging


def main():
    setup_logging()

    logger = logging.getLogger(__name__)
    logger.info("Starting Strava CLI\n")

    token = GetAccessToken()
    access_token = token.get_access_token()

    strava_API_sync = SyncStravaAPI(access_token=access_token)
    strava_API_async = AsyncStravaAPI(
        access_token=access_token,
        deleter=token.supabase_deleter,
        table=token.credentials["supabase_secrets"].SUPABASE_TABLE,
        encryptor=token.encryptor,
    )

    result_console_printer = ResultConsolePrinter()
    error_console_printer = ConsoleErrorHandler()

    service = strava_service.StravaService(strava_API_sync, strava_API_async)

    menu = MenuHandler(
        service=service,
        result_console_printer=result_console_printer,
        error_console_printer=error_console_printer,
    )

    while True:
        menu.print_menu()
        option = input("\nChoose an option (number or 'q' to exit): ")

        if option.lower() == "q":
            print("\n👋 Goodbye")
            break

        menu.execute_option(option)


if __name__ == "__main__":
    main()
