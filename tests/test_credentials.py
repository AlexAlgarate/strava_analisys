import stat
from pathlib import Path

import pytest
from cryptography.fernet import Fernet

from src.infrastructure.auth.credentials import (
    FernetSecrets,
    StravaSecrets,
    get_default_key_path,
    get_default_token_path,
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


def test_default_paths_honor_xdg_directories(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    config_home = tmp_path / "config"
    data_home = tmp_path / "data"
    monkeypatch.setenv("XDG_CONFIG_HOME", str(config_home))
    monkeypatch.setenv("XDG_DATA_HOME", str(data_home))

    assert get_default_key_path() == config_home / "strava-analysis" / "fernet.key"
    assert get_default_token_path() == data_home / "strava-analysis" / "tokens.enc"


def test_fernet_secrets_uses_environment_key(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    key = Fernet.generate_key().decode()
    monkeypatch.setenv("FERNET_KEY", key)

    secrets = FernetSecrets(tmp_path / "unused.key")

    assert secrets.fernet_key == key
    assert secrets.cipher.decrypt(secrets.cipher.encrypt(b"message")) == b"message"
    assert not (tmp_path / "unused.key").exists()


def test_fernet_secrets_creates_and_reuses_private_local_key(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.delenv("FERNET_KEY", raising=False)
    key_path = tmp_path / "config" / "fernet.key"

    first = FernetSecrets(key_path)
    second = FernetSecrets(key_path)

    assert first.fernet_key == second.fernet_key
    assert stat.S_IMODE(key_path.stat().st_mode) == 0o600
    assert stat.S_IMODE(key_path.parent.stat().st_mode) == 0o700


def test_fernet_secrets_rejects_invalid_environment_key(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("FERNET_KEY", "invalid")

    with pytest.raises(ValueError, match="not a valid Fernet key"):
        FernetSecrets(tmp_path / "unused.key")
