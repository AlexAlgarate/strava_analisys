from pathlib import Path
from unittest.mock import Mock

import pytest

from src import composition
from src.application.use_cases.activities import ActivityService
from src.application.use_cases.activity_summary import ActivitySummaryService
from src.application.use_cases.activity_zones import ActivityZonesService
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
    monkeypatch.delenv("FERNET_KEY", raising=False)
    key_path = tmp_path / "key"
    token_path = tmp_path / "token"

    service = composition.build_access_token_service(token_path, key_path)

    assert isinstance(service, AccessTokenService)
    assert key_path.exists()
    assert not token_path.exists()
    load_dotenv.assert_called_once_with()


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
    assert isinstance(services.summary, ActivitySummaryService)


def test_builds_default_export_adapters() -> None:
    services = composition.build_application_services(Mock())

    assert services.stream_export.supported_formats == ("csv",)
    assert isinstance(services.activity_zones._writer, JsonActivityZonesWriter)
