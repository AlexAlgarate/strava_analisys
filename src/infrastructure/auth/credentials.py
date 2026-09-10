import os


def get_env_variable(var_name: str, default_value: str | None = None) -> str:
    value = os.environ.get(var_name, default_value)
    if value is None:
        raise ValueError(f"Environment variable {var_name} is required but not set.")
    return value


class StravaSecrets:
    def __init__(self) -> None:
        self.strava_client_id = get_env_variable("STRAVA_CLIENT_ID")
        self.strava_secret_key = get_env_variable("STRAVA_SECRET_KEY")
