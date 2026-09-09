import logging
import os
from pathlib import Path

from src.access_token import GetAccessToken
from src.core.activities.summary.handlers import ActivitySummaryBuilder
from src.core.activities.summary.service import ActivitySummaryService
from src.core.service import StravaService
from src.infrastructure.api_clients.async_strava_api import AsyncStravaAPI
from src.infrastructure.export.csv_stream_exporter import CsvStreamExporter
from src.infrastructure.export.json_activity_writer import (
    JsonActivityDetailsWriter,
    JsonActivityZonesWriter,
)
from src.infrastructure.persistence.json_activity_loader import JsonActivityLoader
from src.presentation.cli_entrypoint import MenuHandler
from src.presentation.console_output.console_error_handler import (
    ConsoleErrorHandler,
)
from src.presentation.console_output.result_console_printer import (
    ResultConsolePrinter,
)
from src.presentation.console_output.weekly_summary_presenter import (
    ConsoleSummaryPresenter,
)
from src.utils.logger_config import setup_logging


def main() -> None:
    setup_logging()

    logger = logging.getLogger(__name__)
    logger.info("Starting Strava CLI\n")

    token = GetAccessToken()
    access_token = token.get_access_token()

    strava_api = AsyncStravaAPI(
        access_token=access_token,
    )

    result_console_printer = ResultConsolePrinter()
    error_console_printer = ConsoleErrorHandler()

    activities_path = Path("activities.json")
    service = StravaService(
        api=strava_api,
        exporters={"csv": CsvStreamExporter()},
        details_writer=JsonActivityDetailsWriter(activities_path),
        zones_writer=JsonActivityZonesWriter(Path("json_zones_files")),
    )
    summary_service = ActivitySummaryService(
        data_loader=JsonActivityLoader(activities_path),
        summary_builder=ActivitySummaryBuilder(),
        presenter=ConsoleSummaryPresenter(),
    )

    menu = MenuHandler(
        service=service,
        result_console_printer=result_console_printer,
        error_console_printer=error_console_printer,
        summary_service=summary_service,
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
