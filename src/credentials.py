import os

from cryptography.fernet import Fernet


def get_env_variable(var_name: str, default_value: str = None) -> str:
    """
    Retrieves an environment variable with optional default value.

    Args:
        var_name (str): The name of the environment variable.
        default_value (str): The default value if the variable is not found.

    Returns:
        str: The value of the environment variable.

    Raises:
        ValueError: If the environment variable is not found and no default is provided.
    """
    value = os.environ.get(var_name, default_value)
    if value is None:
        raise ValueError(f"Environment variable {var_name} is required but not set.")
    return value


class StravaSecrets:
    def __init__(self):
        self.STRAVA_CLIENT_ID = get_env_variable("STRAVA_CLIENT_ID")
        self.STRAVA_SECRET_KEY = get_env_variable("STRAVA_SECRET_KEY")


class SupabaseSecrets:
    def __init__(self):
        self.SUPABASE_URL = get_env_variable("SUPABASE_URL")
        self.SUPABASE_API_KEY = get_env_variable("SUPABASE_API_KEY")
        self.SUPABASE_TABLE = get_env_variable("SUPABASE_TABLE")


class FernetSecrets:
    def __init__(self):
        self.FERNET_KEY = get_env_variable("FERNET_KEY", Fernet.generate_key().decode())
        self.CIPHER = Fernet(self.FERNET_KEY.encode())
