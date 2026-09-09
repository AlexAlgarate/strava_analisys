import stat
from json import dumps
from pathlib import Path
from unittest.mock import Mock

import pytest
from cryptography.fernet import Fernet

from src.domain.token import TokenSet
from src.infrastructure.persistence.encrypted_file_token_store import (
    EncryptedFileTokenStore,
)
from src.utils.exceptions import TokenStorageError


@pytest.fixture
def token_path(tmp_path: Path) -> Path:
    return tmp_path / "private" / "tokens.enc"


@pytest.fixture
def cipher() -> Fernet:
    return Fernet(Fernet.generate_key())


@pytest.fixture
def store(token_path: Path, cipher: Fernet) -> EncryptedFileTokenStore:
    return EncryptedFileTokenStore(token_path, cipher)


def test_missing_token_file_returns_none(store: EncryptedFileTokenStore) -> None:
    assert store.load() is None


def test_round_trip_is_encrypted_and_private(
    store: EncryptedFileTokenStore, token_path: Path
) -> None:
    tokens = TokenSet("secret-access", "secret-refresh", 2_000_000_000)

    store.save(tokens)

    assert store.load() == tokens
    assert b"secret-access" not in token_path.read_bytes()
    assert stat.S_IMODE(token_path.stat().st_mode) == 0o600
    assert stat.S_IMODE(token_path.parent.stat().st_mode) == 0o700


def test_save_replaces_previous_token(
    store: EncryptedFileTokenStore,
) -> None:
    store.save(TokenSet("first", "refresh-1", 100))
    replacement = TokenSet("second", "refresh-2", 200)

    store.save(replacement)

    assert store.load() == replacement


def test_clear_removes_token_file(
    store: EncryptedFileTokenStore, token_path: Path
) -> None:
    store.save(TokenSet("access", "refresh", 100))

    store.clear()
    store.clear()

    assert not token_path.exists()


def test_corrupt_ciphertext_raises_domain_specific_error(
    store: EncryptedFileTokenStore, token_path: Path
) -> None:
    token_path.parent.mkdir()
    token_path.write_bytes(b"not-encrypted")

    with pytest.raises(TokenStorageError, match="Could not read"):
        store.load()


def test_non_object_payload_raises_domain_specific_error(
    store: EncryptedFileTokenStore, token_path: Path, cipher: Fernet
) -> None:
    token_path.parent.mkdir()
    token_path.write_bytes(cipher.encrypt(dumps([]).encode()))

    with pytest.raises(TokenStorageError, match="Could not read"):
        store.load()


def test_clear_translates_filesystem_error(
    store: EncryptedFileTokenStore, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(Path, "unlink", Mock(side_effect=OSError("permission denied")))

    with pytest.raises(TokenStorageError, match="Could not remove"):
        store.clear()


def test_save_cleans_up_temporary_file_after_failure(
    store: EncryptedFileTokenStore,
    token_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "src.infrastructure.persistence.encrypted_file_token_store.os.replace",
        Mock(side_effect=OSError("permission denied")),
    )

    with pytest.raises(TokenStorageError, match="Could not write"):
        store.save(TokenSet("access", "refresh", 100))

    assert list(token_path.parent.iterdir()) == []
