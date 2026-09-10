from collections.abc import Mapping
from dataclasses import dataclass
from functools import partial
from pathlib import Path

from dotenv import load_dotenv

from src.application.concurrency import DEFAULT_MAX_CONCURRENCY
from src.application.ports.export import ActivityZonesWriter, StreamExporter
from src.application.results import StreamExportResult
from src.application.use_cases.activities import ActivityService
from src.application.use_cases.activity_summary import ActivitySummaryService
from src.application.use_cases.activity_zones import ActivityZonesService
from src.application.use_cases.activity_zones_export import (
    ActivityZonesExportService,
)
from src.application.use_cases.authentication import AccessTokenService
from src.application.use_cases.stream_export import StreamExportService
from src.application.use_cases.streams import ActivityStreamService
from src.domain.activity_stream import ActivityStream, StreamBatch
from src.domain.activity_summary import WeeklyActivitySummary
from src.domain.detailed_activity import DetailedActivity
from src.domain.heart_rate_zones import HeartRateZones
from src.domain.week_period import WeekSelection
from src.infrastructure.api_clients.async_strava_api import AsyncStravaAPI
from src.infrastructure.auth.browser_authorization import (
    BrowserAuthorizationCodeProvider,
    StravaAuthorizationConfig,
)
from src.infrastructure.auth.credentials import (
    StravaSecrets,
)
from src.infrastructure.auth.strava_token_gateway import StravaTokenGateway
from src.infrastructure.export.csv_stream_exporter import CsvStreamExporter
from src.infrastructure.export.json_activity_zones_writer import (
    JsonActivityZonesWriter,
)
from src.infrastructure.persistence.dotenv_token_store import DotenvTokenStore
from src.infrastructure.strava.activity_gateway import StravaActivityGateway
from src.presentation.menu.commands import (
    MenuCommand,
    MenuCommandRegistry,
    with_heading,
)
from src.presentation.menu.options import MenuOption
from src.presentation.ports import PromptReader, ResultPresenter, WeeklySummaryPresenter


@dataclass(frozen=True, slots=True)
class ApplicationServices:
    """Fully wired application use cases exposed to delivery adapters."""

    activities: ActivityService
    streams: ActivityStreamService
    stream_export: StreamExportService
    activity_zones: ActivityZonesService
    activity_zones_export: ActivityZonesExportService
    summary: ActivitySummaryService


def build_access_token_service(
    env_path: Path | None = None,
) -> AccessTokenService:
    """Build the OAuth use case and all of its driven adapters."""
    resolved_env_path = env_path or Path(".env")
    token_store = DotenvTokenStore(resolved_env_path)
    token_store.secure()
    load_dotenv(dotenv_path=resolved_env_path, interpolate=False)
    credentials = StravaSecrets()
    return AccessTokenService(
        token_store=token_store,
        token_gateway=StravaTokenGateway(
            client_id=credentials.strava_client_id,
            secret_key=credentials.strava_secret_key,
        ),
        authorization_code_provider=BrowserAuthorizationCodeProvider(
            StravaAuthorizationConfig(credentials.strava_client_id)
        ),
    )


def build_application_services(
    api: AsyncStravaAPI,
    *,
    exporters: Mapping[str, StreamExporter] | None = None,
    zones_writer: ActivityZonesWriter | None = None,
    max_concurrency: int = DEFAULT_MAX_CONCURRENCY,
) -> ApplicationServices:
    """Build application services around one external activity gateway."""
    gateway = StravaActivityGateway(api)
    activities = ActivityService(
        gateway,
        max_concurrency=max_concurrency,
    )
    streams = ActivityStreamService(
        gateway,
        activities,
        max_concurrency=max_concurrency,
    )
    configured_exporters = (
        exporters if exporters is not None else {"csv": CsvStreamExporter()}
    )
    configured_zones_writer = (
        zones_writer
        if zones_writer is not None
        else JsonActivityZonesWriter(Path("json_zones_files"))
    )
    activity_zones = ActivityZonesService(gateway)
    return ApplicationServices(
        activities=activities,
        streams=streams,
        stream_export=StreamExportService(streams, configured_exporters),
        activity_zones=activity_zones,
        activity_zones_export=ActivityZonesExportService(
            activity_zones,
            configured_zones_writer,
        ),
        summary=ActivitySummaryService(activities),
    )


def build_menu_commands(
    services: ApplicationServices,
    *,
    prompts: PromptReader,
    result_presenter: ResultPresenter,
    summary_presenter: WeeklySummaryPresenter,
) -> MenuCommandRegistry:
    """Compose the commands exposed by the default terminal interface."""

    async def get_single_stream() -> ActivityStream:
        activity_id = prompts.ask_activity_id()
        return await services.streams.get_streams_for_activity(activity_id)

    async def get_multiple_streams() -> StreamBatch:
        activity_ids = prompts.ask_activity_ids()
        return await services.streams.get_streams_for_multiple_activities(activity_ids)

    async def get_activity_zones() -> HeartRateZones:
        activity_id = prompts.ask_activity_id()
        return await services.activity_zones.get_activity_zones(activity_id)

    return MenuCommandRegistry(
        (
            MenuCommand[list[DetailedActivity]](
                option=MenuOption.ACTIVITY_DETAILS,
                action=partial(
                    services.activities.get_activity_details,
                    week=WeekSelection.CURRENT,
                ),
                presenter=with_heading(
                    MenuOption.ACTIVITY_DETAILS.description,
                    result_presenter.present_heading,
                    result_presenter.present_detailed_activities,
                ),
            ),
            MenuCommand[list[DetailedActivity]](
                option=MenuOption.ACTIVITY_DETAILS_PREV_WEEK,
                action=partial(
                    services.activities.get_activity_details,
                    week=WeekSelection.PREVIOUS,
                ),
                presenter=with_heading(
                    MenuOption.ACTIVITY_DETAILS_PREV_WEEK.description,
                    result_presenter.present_heading,
                    result_presenter.present_detailed_activities,
                ),
            ),
            MenuCommand[list[DetailedActivity]](
                option=MenuOption.ACTIVITY_RANGE,
                action=partial(
                    services.activities.get_activity_range,
                    week=WeekSelection.CURRENT,
                ),
                presenter=with_heading(
                    MenuOption.ACTIVITY_RANGE.description,
                    result_presenter.present_heading,
                    result_presenter.present_activity_list,
                ),
            ),
            MenuCommand[list[DetailedActivity]](
                option=MenuOption.ACTIVITY_RANGE_PREV_WEEK,
                action=partial(
                    services.activities.get_activity_range,
                    week=WeekSelection.PREVIOUS,
                ),
                presenter=with_heading(
                    MenuOption.ACTIVITY_RANGE_PREV_WEEK.description,
                    result_presenter.present_heading,
                    result_presenter.present_activity_list,
                ),
            ),
            MenuCommand[ActivityStream](
                option=MenuOption.SINGLE_STREAM,
                action=get_single_stream,
                presenter=with_heading(
                    MenuOption.SINGLE_STREAM.description,
                    result_presenter.present_heading,
                    result_presenter.present_activity_stream,
                ),
            ),
            MenuCommand[StreamBatch](
                option=MenuOption.MULTIPLE_STREAMS,
                action=get_multiple_streams,
                presenter=with_heading(
                    MenuOption.MULTIPLE_STREAMS.description,
                    result_presenter.present_heading,
                    result_presenter.present_stream_batch,
                ),
            ),
            MenuCommand[StreamExportResult](
                option=MenuOption.STREAMS_CURRENT_WEEK,
                action=partial(
                    services.stream_export.export_streams_for_selected_week,
                    week=WeekSelection.CURRENT,
                ),
                presenter=with_heading(
                    MenuOption.STREAMS_CURRENT_WEEK.description,
                    result_presenter.present_heading,
                    result_presenter.present_stream_export,
                ),
            ),
            MenuCommand[StreamExportResult](
                option=MenuOption.STREAMS_PREV_WEEK,
                action=partial(
                    services.stream_export.export_streams_for_selected_week,
                    week=WeekSelection.PREVIOUS,
                ),
                presenter=with_heading(
                    MenuOption.STREAMS_PREV_WEEK.description,
                    result_presenter.present_heading,
                    result_presenter.present_stream_export,
                ),
            ),
            MenuCommand[WeeklyActivitySummary](
                option=MenuOption.WEEKLY_REPORT,
                action=partial(
                    services.summary.generate_summary,
                    week=WeekSelection.CURRENT,
                ),
                presenter=summary_presenter.present_weekly_report,
            ),
            MenuCommand[HeartRateZones](
                option=MenuOption.ACTIVITY_ZONES,
                action=get_activity_zones,
                presenter=with_heading(
                    MenuOption.ACTIVITY_ZONES.description,
                    result_presenter.present_heading,
                    result_presenter.present_activity_zones,
                ),
            ),
        )
    )
