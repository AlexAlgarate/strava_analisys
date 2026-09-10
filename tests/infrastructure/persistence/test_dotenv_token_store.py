import json
import stat
from pathlib import Path
from unittest.mock import Mock

import pytest
from dotenv import dotenv_values

from src.application.errors import TokenStorageError
from src.domain.token import TokenSet
from src.infrastructure.persistence.dotenv_token_store import (
    TOKEN_ENV_VARIABLE,
    DotenvTokenStore,
)


@pytest.fixture
def env_path(tmp_path: Path) -> Path:
    return tmp_path / "project" / ".env"


@pytest.fixture
def store(
    env_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> DotenvTokenStore:
    monkeypatch.delenv(TOKEN_ENV_VARIABLE, raising=False)
    return DotenvTokenStore(env_path)


def test_missing_token_returns_none(store: DotenvTokenStore) -> None:
    assert store.load() is None


def test_empty_token_variable_returns_none(
    store: DotenvTokenStore,
    env_path: Path,
) -> None:
    env_path.parent.mkdir()
    env_path.write_text(f"{TOKEN_ENV_VARIABLE}=\n", encoding="utf-8")

    assert store.load() is None


def test_round_trip_uses_private_env_file(
    store: DotenvTokenStore,
    env_path: Path,
) -> None:
    tokens = TokenSet("secret-access", "secret-refresh", 2_000_000_000)

    store.save(tokens)

    assert store.load() == tokens
    assert "secret-access" in env_path.read_text(encoding="utf-8")
    assert stat.S_IMODE(env_path.stat().st_mode) == 0o600


def test_load_restricts_existing_env_file_permissions(
    store: DotenvTokenStore,
    env_path: Path,
) -> None:
    env_path.parent.mkdir()
    env_path.write_text("STRAVA_CLIENT_ID=123\n", encoding="utf-8")
    env_path.chmod(0o664)

    assert store.load() is None
    assert stat.S_IMODE(env_path.stat().st_mode) == 0o600


def test_save_preserves_existing_environment_values(
    store: DotenvTokenStore,
    env_path: Path,
) -> None:
    env_path.parent.mkdir()
    env_path.write_text("# Local settings\nSTRAVA_CLIENT_ID=123\n", encoding="utf-8")

    store.save(TokenSet("access", "refresh", 100))

    contents = env_path.read_text(encoding="utf-8")
    assert "# Local settings" in contents
    assert dotenv_values(env_path)["STRAVA_CLIENT_ID"] == "123"


def test_save_replaces_previous_token(store: DotenvTokenStore) -> None:
    store.save(TokenSet("first", "refresh-1", 100))
    replacement = TokenSet("second", "refresh-2", 200)

    store.save(replacement)

    assert store.load() == replacement


def test_clear_removes_only_token_variable(
    store: DotenvTokenStore,
    env_path: Path,
) -> None:
    env_path.parent.mkdir()
    env_path.write_text("STRAVA_CLIENT_ID=123\n", encoding="utf-8")
    store.save(TokenSet("access", "refresh", 100))

    store.clear()
    store.clear()

    assert store.load() is None
    assert dotenv_values(env_path)["STRAVA_CLIENT_ID"] == "123"
    assert TOKEN_ENV_VARIABLE not in dotenv_values(env_path)


def test_loads_token_from_process_environment(
    store: DotenvTokenStore,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    serialized_token = json.dumps(
        {
            "access_token": "access",
            "refresh_token": "refresh",
            "expires_at": 100,
        }
    )
    monkeypatch.setenv(TOKEN_ENV_VARIABLE, serialized_token)

    assert store.load() == TokenSet("access", "refresh", 100)


@pytest.mark.parametrize("serialized_token", ["not-json", "[]"])
def test_invalid_token_raises_domain_specific_error(
    store: DotenvTokenStore,
    env_path: Path,
    serialized_token: str,
) -> None:
    env_path.parent.mkdir()
    env_path.write_text(
        f"{TOKEN_ENV_VARIABLE}='{serialized_token}'\n",
        encoding="utf-8",
    )

    with pytest.raises(TokenStorageError, match="Could not read"):
        store.load()


def test_load_translates_filesystem_error(
    store: DotenvTokenStore,
    env_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    env_path.parent.mkdir()
    env_path.touch()
    monkeypatch.setattr(
        "src.infrastructure.persistence.dotenv_token_store.dotenv_values",
        Mock(side_effect=OSError("permission denied")),
    )

    with pytest.raises(TokenStorageError, match="Could not read"):
        store.load()


def test_save_translates_write_error(
    store: DotenvTokenStore,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "src.infrastructure.persistence.dotenv_token_store.set_key",
        Mock(side_effect=OSError("read-only filesystem")),
    )

    with pytest.raises(TokenStorageError, match="Could not write"):
        store.save(TokenSet("access", "refresh", 100))


def test_clear_translates_write_error(
    store: DotenvTokenStore,
    env_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store.save(TokenSet("access", "refresh", 100))
    monkeypatch.setattr(
        "src.infrastructure.persistence.dotenv_token_store.unset_key",
        Mock(side_effect=OSError("read-only filesystem")),
    )

    with pytest.raises(TokenStorageError, match="Could not remove"):
        store.clear()
