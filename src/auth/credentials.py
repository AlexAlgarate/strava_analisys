import os

from cryptography.fernet import Fernet


def get_env_variable(var_name: str, default_value: str | None = None) -> str:
    value = os.environ.get(var_name, default_value)
    if value is None:
        raise ValueError(f"Environment variable {var_name} is required but not set.")
    return value


class StravaSecrets:
    def __init__(self):
        self.strava_client_id = get_env_variable("STRAVA_CLIENT_ID")
        self.strava_secret_key = get_env_variable("STRAVA_SECRET_KEY")


class SupabaseSecrets:
    def __init__(self):
        self.supabase_url = get_env_variable("SUPABASE_URL")
        if self.supabase_url.startswith("https\\x3a"):
            self.supabase_url = self.supabase_url.replace("https\\x3a", "https:")
        self.supabase_api_key = get_env_variable("SUPABASE_API_KEY")
        self.supabase_table = get_env_variable("SUPABASE_TABLE")


class FernetSecrets:
    def __init__(self):
        self.fernet_key = get_env_variable("FERNET_KEY", Fernet.generate_key().decode())
        self.cipher = Fernet(self.fernet_key.encode())
