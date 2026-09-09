import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Final, cast

from cryptography.fernet import Fernet, InvalidToken

from src.domain.token import TokenSet
from src.utils.exceptions import TokenStorageError

_PRIVATE_DIRECTORY_MODE: Final = 0o700
_PRIVATE_FILE_MODE: Final = 0o600


class EncryptedFileTokenStore:
    """Persist the current token set in one local Fernet-encrypted file."""

    def __init__(self, path: Path, cipher: Fernet) -> None:
        self._path = path
        self._cipher = cipher

    def load(self) -> TokenSet | None:
        if not self._path.exists():
            return None

        try:
            plaintext = self._cipher.decrypt(self._path.read_bytes())
            payload = json.loads(plaintext)
            if not isinstance(payload, dict):
                raise TypeError("Token payload must be a JSON object.")
            return TokenSet.from_mapping(cast(dict[str, object], payload))
        except (
            OSError,
            InvalidToken,
            UnicodeDecodeError,
            json.JSONDecodeError,
            TypeError,
            ValueError,
        ) as exc:
            raise TokenStorageError(
                f"Could not read the encrypted token file at {self._path}."
            ) from exc

    def save(self, tokens: TokenSet) -> None:
        payload = json.dumps(tokens.as_dict(), separators=(",", ":")).encode()
        self._write_private_file(self._cipher.encrypt(payload))

    def clear(self) -> None:
        try:
            self._path.unlink(missing_ok=True)
        except OSError as exc:
            raise TokenStorageError(
                f"Could not remove the token file at {self._path}."
            ) from exc

    def _write_private_file(self, content: bytes) -> None:
        temp_path: Path | None = None
        try:
            self._path.parent.mkdir(
                mode=_PRIVATE_DIRECTORY_MODE, parents=True, exist_ok=True
            )
            self._path.parent.chmod(_PRIVATE_DIRECTORY_MODE)
            with NamedTemporaryFile(dir=self._path.parent, delete=False) as temp_file:
                temp_path = Path(temp_file.name)
                temp_file.write(content)
            temp_path.chmod(_PRIVATE_FILE_MODE)
            os.replace(temp_path, self._path)
            self._path.chmod(_PRIVATE_FILE_MODE)
        except OSError as exc:
            if temp_path is not None:
                try:
                    temp_path.unlink(missing_ok=True)
                except OSError as cleanup_error:
                    exc.add_note(
                        f"Could not remove temporary token file {temp_path}: "
                        f"{cleanup_error}"
                    )
            raise TokenStorageError(
                f"Could not write the encrypted token file at {self._path}."
            ) from exc
