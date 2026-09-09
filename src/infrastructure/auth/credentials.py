import os
from pathlib import Path

from cryptography.fernet import Fernet

APP_DIRECTORY = "strava-analysis"


def get_env_variable(var_name: str, default_value: str | None = None) -> str:
    value = os.environ.get(var_name, default_value)
    if value is None:
        raise ValueError(f"Environment variable {var_name} is required but not set.")
    return value


class StravaSecrets:
    def __init__(self) -> None:
        self.strava_client_id = get_env_variable("STRAVA_CLIENT_ID")
        self.strava_secret_key = get_env_variable("STRAVA_SECRET_KEY")


def get_default_key_path() -> Path:
    config_home = os.environ.get("XDG_CONFIG_HOME")
    root = Path(config_home) if config_home else Path.home() / ".config"
    return root / APP_DIRECTORY / "fernet.key"


def get_default_token_path() -> Path:
    data_home = os.environ.get("XDG_DATA_HOME")
    root = Path(data_home) if data_home else Path.home() / ".local" / "share"
    return root / APP_DIRECTORY / "tokens.enc"


class FernetSecrets:
    def __init__(self, key_path: Path | None = None) -> None:
        configured_key = os.environ.get("FERNET_KEY")
        key = (
            configured_key.encode()
            if configured_key is not None
            else self._load_or_create_key(key_path or get_default_key_path())
        )
        try:
            self.cipher = Fernet(key)
        except (TypeError, ValueError) as exc:
            raise ValueError("FERNET_KEY is not a valid Fernet key.") from exc
        self.fernet_key = key.decode()

    @staticmethod
    def _load_or_create_key(path: Path) -> bytes:
        if path.exists():
            return FernetSecrets._read_private_key(path)

        key = Fernet.generate_key()
        try:
            path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
            path.parent.chmod(0o700)
            file_descriptor = os.open(
                path,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                0o600,
            )
            with os.fdopen(file_descriptor, "wb") as key_file:
                key_file.write(key)
        except FileExistsError:
            return FernetSecrets._read_private_key(path)
        except OSError as exc:
            raise ValueError(f"Could not store the Fernet key at {path}.") from exc
        return key

    @staticmethod
    def _read_private_key(path: Path) -> bytes:
        try:
            path.parent.chmod(0o700)
            key = path.read_bytes().strip()
            path.chmod(0o600)
            return key
        except OSError as exc:
            raise ValueError(f"Could not read the Fernet key at {path}.") from exc
