import json
import os
from pathlib import Path
from typing import Final

from dotenv import dotenv_values, set_key, unset_key

from src.application.errors import TokenStorageError
from src.domain.token import TokenSet
from src.infrastructure.serialization.token import token_from_mapping, token_to_mapping

TOKEN_ENV_VARIABLE: Final = "STRAVA_OAUTH_TOKEN"
_PRIVATE_FILE_MODE: Final = 0o600


class DotenvTokenStore:
    """Persist the current OAuth token set in a project-local dotenv file."""

    def __init__(self, path: Path) -> None:
        self._path = path

    def load(self) -> TokenSet | None:
        try:
            serialized_token = self._read_token_value()
            if serialized_token is None:
                return None
            return token_from_mapping(json.loads(serialized_token))
        except (
            OSError,
            UnicodeDecodeError,
            json.JSONDecodeError,
            TypeError,
            ValueError,
        ) as exc:
            raise TokenStorageError(
                f"Could not read the OAuth token from {self._path}."
            ) from exc

    def save(self, tokens: TokenSet) -> None:
        serialized_token = json.dumps(
            token_to_mapping(tokens),
            separators=(",", ":"),
        )
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            success, _, _ = set_key(
                self._path,
                TOKEN_ENV_VARIABLE,
                serialized_token,
            )
            if success is not True:
                raise OSError("python-dotenv could not update the token variable.")
            self._path.chmod(_PRIVATE_FILE_MODE)
        except (OSError, UnicodeError) as exc:
            raise TokenStorageError(
                f"Could not write the OAuth token to {self._path}."
            ) from exc

    def clear(self) -> None:
        try:
            if self._path.exists():
                values = dotenv_values(self._path, interpolate=False)
                if TOKEN_ENV_VARIABLE in values:
                    success, _ = unset_key(self._path, TOKEN_ENV_VARIABLE)
                    if success is not True:
                        raise OSError(
                            "python-dotenv could not remove the token variable."
                        )
                    self._path.chmod(_PRIVATE_FILE_MODE)
            os.environ.pop(TOKEN_ENV_VARIABLE, None)
        except (OSError, UnicodeError) as exc:
            raise TokenStorageError(
                f"Could not remove the OAuth token from {self._path}."
            ) from exc

    def _read_token_value(self) -> str | None:
        if self._path.exists():
            self._path.chmod(_PRIVATE_FILE_MODE)
            values = dotenv_values(self._path, interpolate=False)
            if TOKEN_ENV_VARIABLE in values:
                return values[TOKEN_ENV_VARIABLE] or None
        return os.environ.get(TOKEN_ENV_VARIABLE) or None
