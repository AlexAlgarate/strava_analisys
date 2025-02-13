import os
from typing import Generator

import pytest
from cryptography.fernet import Fernet

from src.credentials import (
    FernetSecrets,
    StravaSecrets,
    SupabaseSecrets,
    get_env_variable,
)


@pytest.fixture
def environment_setup() -> Generator:
    """
    Fixture to set up and tear down environment variables for testing.
    Uses a generator pattern to handle cleanup after tests.
    """
    original_env = {
        key: os.environ.get(key)
        for key in [
            "STRAVA_CLIENT_ID",
            "STRAVA_SECRET_KEY",
            "SUPABASE_URL",
            "SUPABASE_API_KEY",
            "SUPABASE_TABLE",
            "FERNET_KEY",
        ]
    }

    test_values = {
        "STRAVA_CLIENT_ID": "test_strava_id",
        "STRAVA_SECRET_KEY": "test_strava_secret",
        "SUPABASE_URL": "https://test.supabase.co",
        "SUPABASE_API_KEY": "test_supabase_key",
        "SUPABASE_TABLE": "test_table",
        "FERNET_KEY": Fernet.generate_key().decode(),
    }

    for key, value in test_values.items():
        os.environ[key] = value

    yield test_values

    # Cleanup: restore original environment
    for key, value in original_env.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value


def test_get_env_variable_success():
    """Test successful retrieval of environment variable."""
    os.environ["TEST_VAR"] = "test_value"
    assert get_env_variable("TEST_VAR") == "test_value"
    os.environ.pop("TEST_VAR")


def test_get_env_variable_with_default():
    """Test retrieval with default value when variable is not set."""
    assert get_env_variable("NONEXISTENT_VAR", "default_value") == "default_value"


def test_get_env_variable_raises_error():
    """Test that ValueError is raised when variable is not found and no default provided."""
    with pytest.raises(ValueError) as exc_info:
        get_env_variable("NONEXISTENT_VAR")
    assert "Environment variable NONEXISTENT_VAR is required but not set" in str(
        exc_info.value
    )


def test_strava_secrets(environment_setup):
    """Test StravaSecrets class initialization and attribute access."""
    secrets = StravaSecrets()
    assert secrets.STRAVA_CLIENT_ID == environment_setup["STRAVA_CLIENT_ID"]
    assert secrets.STRAVA_SECRET_KEY == environment_setup["STRAVA_SECRET_KEY"]


def test_supabase_secrets(environment_setup):
    """Test SupabaseSecrets class initialization and attribute access."""
    secrets = SupabaseSecrets()
    assert secrets.SUPABASE_URL == environment_setup["SUPABASE_URL"]
    assert secrets.SUPABASE_API_KEY == environment_setup["SUPABASE_API_KEY"]
    assert secrets.SUPABASE_TABLE == environment_setup["SUPABASE_TABLE"]


def test_fernet_secrets_with_env_key(environment_setup):
    """Test FernetSecrets class with pre-set environment key."""
    secrets = FernetSecrets()
    assert secrets.FERNET_KEY == environment_setup["FERNET_KEY"]
    assert isinstance(secrets.CIPHER, Fernet)


def test_fernet_secrets_auto_generation():
    """Test FernetSecrets class with auto-generated key."""
    # Remove any existing FERNET_KEY from environment
    if "FERNET_KEY" in os.environ:
        del os.environ["FERNET_KEY"]

    secrets = FernetSecrets()
    assert secrets.FERNET_KEY is not None
    assert isinstance(secrets.CIPHER, Fernet)

    # Test that the cipher can actually encrypt and decrypt
    test_message = b"Hello, World!"
    encrypted = secrets.CIPHER.encrypt(test_message)
    decrypted = secrets.CIPHER.decrypt(encrypted)
    assert decrypted == test_message
