import asyncio
import logging

from src.composition import build_access_token_service, build_application_services
from src.infrastructure.api_clients.async_strava_api import AsyncStravaAPI
from src.infrastructure.logging import setup_logging
from src.presentation.cli_entrypoint import MenuDependencies, MenuHandler
from src.presentation.console_output.console import create_console
from src.presentation.console_output.console_error_handler import (
    ConsoleErrorHandler,
)
from src.presentation.console_output.progress import ConsoleProgress
from src.presentation.console_output.prompts import ConsolePrompts
from src.presentation.console_output.result_console_printer import (
    ResultConsolePrinter,
)
from src.presentation.console_output.weekly_summary_presenter import (
    ConsoleSummaryPresenter,
)
from src.presentation.menu.renderer import MenuRenderer


async def run_cli() -> None:
    setup_logging()

    logger = logging.getLogger(__name__)
    logger.info("Starting Strava CLI\n")

    access_token = build_access_token_service().get_access_token()

    async with AsyncStravaAPI(access_token=access_token) as strava_api:
        console = create_console()
        prompts = ConsolePrompts(console)
        result_console_printer = ResultConsolePrinter(console)
        error_console_printer = ConsoleErrorHandler(console)

        services = build_application_services(strava_api)

        menu = MenuHandler(
            MenuDependencies(
                activities=services.activities,
                streams=services.streams,
                stream_export=services.stream_export,
                activity_zones=services.activity_zones,
                summary=services.summary,
                result_printer=result_console_printer,
                error_printer=error_console_printer,
                summary_presenter=ConsoleSummaryPresenter(console),
                prompts=prompts,
                menu_view=MenuRenderer(console),
                progress=ConsoleProgress(console),
            )
        )

        menu.print_welcome()
        try:
            while True:
                menu.print_menu()
                option = menu.ask_option()
                if option == "q":
                    break
                await menu.execute_option(option)
        except (EOFError, KeyboardInterrupt):
            pass
        finally:
            menu.print_goodbye()


def main() -> None:
    asyncio.run(run_cli())


if __name__ == "__main__":
    main()
