import logging
import os

from src import strava_service
from src.access_token import GetAccessToken
from src.infrastructure.api_clients.async_strava_api import AsyncStravaAPI
from src.presentation.cli_entrypoint import MenuHandler
from src.presentation.console_output.console_error_handler import ConsoleErrorHandler
from src.presentation.console_output.result_console_printer import ResultConsolePrinter
from src.utils.logger_config import setup_logging


def main() -> None:
    setup_logging()

    logger = logging.getLogger(__name__)
    logger.info("Starting Strava CLI\n")

    token = GetAccessToken()
    access_token = token.get_access_token()

    strava_API_async = AsyncStravaAPI(
        access_token=access_token,  # type: ignore
        deleter=token.supabase_deleter,
        table=token.credentials["supabase_secrets"].supabase_table,
        encryptor=token.encryptor,
    )

    result_console_printer = ResultConsolePrinter()
    error_console_printer = ConsoleErrorHandler()

    service = strava_service.StravaService(api_async=strava_API_async)

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

        _remove_testing_files(option, "e")

        menu.execute_option(option)


def _remove_testing_files(option: str, default_letter: str) -> None:
    if option.lower() == default_letter:
        current_week = "streams_current_week.csv"
        previous_week = "streams_previous_week.csv"
        for file in (current_week, previous_week):
            if os.path.exists(file):
                os.remove(file)
                print(f"Deleted file: {file}")


if __name__ == "__main__":
    main()
