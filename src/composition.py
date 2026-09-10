from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

from src.application.concurrency import DEFAULT_MAX_CONCURRENCY
from src.application.ports.export import ActivityZonesWriter, StreamExporter
from src.application.use_cases.activities import ActivityService
from src.application.use_cases.activity_summary import ActivitySummaryService
from src.application.use_cases.activity_zones import ActivityZonesService
from src.application.use_cases.authentication import AccessTokenService
from src.application.use_cases.stream_export import StreamExportService
from src.application.use_cases.streams import ActivityStreamService
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


@dataclass(frozen=True, slots=True)
class ApplicationServices:
    """Fully wired application use cases exposed to delivery adapters."""

    activities: ActivityService
    streams: ActivityStreamService
    stream_export: StreamExportService
    activity_zones: ActivityZonesService
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
    return ApplicationServices(
        activities=activities,
        streams=streams,
        stream_export=StreamExportService(streams, configured_exporters),
        activity_zones=ActivityZonesService(gateway, configured_zones_writer),
        summary=ActivitySummaryService(activities),
    )
