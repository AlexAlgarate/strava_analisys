import stat
from pathlib import Path
from unittest.mock import Mock

import pytest

from src import composition
from src.application.use_cases.activities import ActivityService
from src.application.use_cases.activity_summary import ActivitySummaryService
from src.application.use_cases.activity_zones import ActivityZonesService
from src.application.use_cases.activity_zones_export import (
    ActivityZonesExportService,
)
from src.application.use_cases.authentication import AccessTokenService
from src.application.use_cases.stream_export import StreamExportService
from src.application.use_cases.streams import ActivityStreamService
from src.infrastructure.export.json_activity_zones_writer import (
    JsonActivityZonesWriter,
)


def test_builds_local_token_service(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    load_dotenv = Mock()
    monkeypatch.setattr(composition, "load_dotenv", load_dotenv)
    monkeypatch.setenv("STRAVA_CLIENT_ID", "client-id")
    monkeypatch.setenv("STRAVA_SECRET_KEY", "secret")
    env_path = tmp_path / ".env"

    service = composition.build_access_token_service(env_path)

    assert isinstance(service, AccessTokenService)
    load_dotenv.assert_called_once_with(dotenv_path=env_path, interpolate=False)


def test_secures_local_env_before_loading_credentials(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    env_path = tmp_path / ".env"
    env_path.write_text(
        "STRAVA_CLIENT_ID=client-id\nSTRAVA_SECRET_KEY=secret\n",
        encoding="utf-8",
    )
    env_path.chmod(0o664)

    def assert_private_file_before_loading(**_kwargs: object) -> None:
        assert stat.S_IMODE(env_path.stat().st_mode) == 0o600

    monkeypatch.setattr(composition, "load_dotenv", assert_private_file_before_loading)
    monkeypatch.setenv("STRAVA_CLIENT_ID", "client-id")
    monkeypatch.setenv("STRAVA_SECRET_KEY", "secret")

    composition.build_access_token_service(env_path)


def test_builds_application_services() -> None:
    services = composition.build_application_services(
        Mock(),
        exporters={"csv": Mock()},
        zones_writer=Mock(),
    )

    assert isinstance(services.activities, ActivityService)
    assert isinstance(services.streams, ActivityStreamService)
    assert isinstance(services.stream_export, StreamExportService)
    assert isinstance(services.activity_zones, ActivityZonesService)
    assert isinstance(services.activity_zones_export, ActivityZonesExportService)
    assert isinstance(services.summary, ActivitySummaryService)


def test_builds_default_export_adapters() -> None:
    services = composition.build_application_services(Mock())

    assert services.stream_export.supported_formats == ("csv",)
    assert isinstance(
        services.activity_zones_export._writer,
        JsonActivityZonesWriter,
    )
