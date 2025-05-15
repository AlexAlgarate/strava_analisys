import os

from cryptography.fernet import Fernet


def get_env_variable(var_name: str, default_value: str | None = None) -> str:
    value = os.environ.get(var_name, default_value)
    if value is None:
        raise ValueError(
            f"Environment variable {var_name} is required but not set."
        )
    return value


class StravaSecrets:
    def __init__(self) -> None:
        self.strava_client_id = get_env_variable("STRAVA_CLIENT_ID")
        self.strava_secret_key = get_env_variable("STRAVA_SECRET_KEY")


class SupabaseSecrets:
    MALFORMED_PREFIX = "https\\x3a"
    CORRECT_PREFIX = "https:"

    def __init__(self) -> None:
        raw_url = get_env_variable("SUPABASE_URL")
        self.supabase_url = self._fix_malformed_url(raw_url)
        self.supabase_api_key = get_env_variable("SUPABASE_API_KEY")
        self.supabase_table = get_env_variable("SUPABASE_TABLE")
        self._validate_credentials()

    def _fix_malformed_url(self, url: str) -> str:
        if url.startswith(self.MALFORMED_PREFIX):
            return url.replace(self.MALFORMED_PREFIX, self.CORRECT_PREFIX)
        return url

    def _validate_credentials(self) -> None:
        if not self.supabase_url.startswith(("http://", "https://")):
            raise ValueError(
                f"Invalid Supabase URL format: {self.supabase_url}"
            )

        if not self.supabase_api_key:
            raise ValueError("Supabase API key cannot be empty")


class FernetSecrets:
    def __init__(self) -> None:
        generate_fernet_key = Fernet.generate_key().decode()
        self.fernet_key = get_env_variable("FERNET_KEY", generate_fernet_key)
        encode_fernet_key = self.fernet_key.encode()
        self.cipher = Fernet(encode_fernet_key)
