import os
from typing import Generator

import pytest
from cryptography.fernet import Fernet

from src.infrastructure.auth.credentials import (
    FernetSecrets,
    StravaSecrets,
    SupabaseSecrets,
    get_env_variable,
)


@pytest.fixture
def environment_setup() -> Generator[dict, None, None]:
    env_vars = [
        "STRAVA_CLIENT_ID",
        "STRAVA_SECRET_KEY",
        "SUPABASE_URL",
        "SUPABASE_API_KEY",
        "SUPABASE_TABLE",
        "FERNET_KEY",
    ]

    original_env = {key: os.environ.get(key) for key in env_vars}

    test_values = {
        "STRAVA_CLIENT_ID": "test_strava_id",
        "STRAVA_SECRET_KEY": "test_strava_secret",
        "SUPABASE_URL": "https://test.supabase.co",
        "SUPABASE_API_KEY": "test_supabase_key",
        "SUPABASE_TABLE": "test_table",
        "FERNET_KEY": Fernet.generate_key().decode(),
    }

    os.environ.update(test_values)

    yield test_values

    for key, value in original_env.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value


class TestCredentials:
    @pytest.mark.parametrize(
        "var_name, var_value",
        [
            ("TEST_VAR", "test_value"),
            ("ANOTHER_TEST_VAR", "another_test_value"),
        ],
    )
    def test_get_env_variable_success(
        self, var_name: str, var_value: str
    ) -> None:
        os.environ[var_name] = var_value
        assert get_env_variable(var_name) == var_value
        os.environ.pop(var_name)

    def test_get_env_variable_with_default(self) -> None:
        assert (
            get_env_variable("NONEXISTENT_VAR", "default_value")
            == "default_value"
        )

    def test_get_env_variable_raises_error(self) -> None:
        with pytest.raises(ValueError) as exc_info:
            get_env_variable("NONEXISTENT_VAR")
        assert (
            "Environment variable NONEXISTENT_VAR is required but not set"
            in str(exc_info.value)
        )

    def test_strava_secrets(self, environment_setup: dict) -> None:
        secrets = StravaSecrets()
        assert secrets.strava_client_id == environment_setup["STRAVA_CLIENT_ID"]
        assert (
            secrets.strava_secret_key == environment_setup["STRAVA_SECRET_KEY"]
        )

    def test_supabase_secrets(self, environment_setup: dict) -> None:
        secrets = SupabaseSecrets()
        assert secrets.supabase_url == environment_setup["SUPABASE_URL"]
        assert secrets.supabase_api_key == environment_setup["SUPABASE_API_KEY"]
        assert secrets.supabase_table == environment_setup["SUPABASE_TABLE"]

    def test_fernet_secrets_with_env_key(self, environment_setup: dict) -> None:
        secrets = FernetSecrets()
        assert secrets.fernet_key == environment_setup["FERNET_KEY"]
        assert isinstance(secrets.cipher, Fernet)

    def test_fernet_secrets_auto_generation(self) -> None:
        if "FERNET_KEY" in os.environ:
            del os.environ["FERNET_KEY"]

        secrets = FernetSecrets()
        assert secrets.fernet_key is not None
        assert isinstance(secrets.cipher, Fernet)

        test_message = b"Hello, World!"
        encrypted = secrets.cipher.encrypt(test_message)
        decrypted = secrets.cipher.decrypt(encrypted)
        assert decrypted == test_message
