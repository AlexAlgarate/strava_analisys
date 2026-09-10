import pytest

from src.infrastructure.auth.credentials import (
    StravaSecrets,
    get_env_variable,
)


class TestGetEnvVariable:
    def test_returns_configured_value(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("TEST_VAR", "test-value")

        assert get_env_variable("TEST_VAR") == "test-value"

    def test_returns_default_value(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("MISSING_TEST_VAR", raising=False)

        assert get_env_variable("MISSING_TEST_VAR", "default") == "default"

    def test_raises_when_required_value_is_missing(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("MISSING_TEST_VAR", raising=False)

        with pytest.raises(ValueError, match="MISSING_TEST_VAR"):
            get_env_variable("MISSING_TEST_VAR")


def test_strava_secrets_load_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("STRAVA_CLIENT_ID", "client-id")
    monkeypatch.setenv("STRAVA_SECRET_KEY", "client-secret")

    secrets = StravaSecrets()

    assert secrets.strava_client_id == "client-id"
    assert secrets.strava_secret_key == "client-secret"
