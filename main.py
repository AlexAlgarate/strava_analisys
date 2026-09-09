import asyncio
import logging
from pathlib import Path

from src.access_token import GetAccessToken
from src.core.activities.summary.service import ActivitySummaryService
from src.core.service import StravaService
from src.infrastructure.api_clients.async_strava_api import AsyncStravaAPI
from src.infrastructure.export.csv_stream_exporter import CsvStreamExporter
from src.infrastructure.export.json_activity_zones_writer import (
    JsonActivityZonesWriter,
)
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


async def run_cli() -> None:
    setup_logging()

    logger = logging.getLogger(__name__)
    logger.info("Starting Strava CLI\n")

    token = GetAccessToken()
    access_token = token.get_access_token()

    async with AsyncStravaAPI(access_token=access_token) as strava_api:
        result_console_printer = ResultConsolePrinter()
        error_console_printer = ConsoleErrorHandler()

        service = StravaService(
            api=strava_api,
            exporters={"csv": CsvStreamExporter()},
            zones_writer=JsonActivityZonesWriter(Path("json_zones_files")),
        )
        summary_service = ActivitySummaryService(activity_provider=service)

        menu = MenuHandler(
            service=service,
            result_console_printer=result_console_printer,
            error_console_printer=error_console_printer,
            summary_service=summary_service,
            summary_presenter=ConsoleSummaryPresenter(),
        )

        while True:
            menu.print_menu()
            option = input("\nChoose an option (number or 'q' to exit): ")

            if option.lower() == "q":
                print("\n👋 Goodbye")
                break

            await menu.execute_option(option)


def main() -> None:
    asyncio.run(run_cli())


if __name__ == "__main__":
    main()
