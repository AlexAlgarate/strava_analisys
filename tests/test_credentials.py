import pytest
from cryptography.fernet import Fernet

from src.infrastructure.auth.credentials import (
    FernetSecrets,
    StravaSecrets,
    SupabaseSecrets,
    get_env_variable,
)


class TestGetEnvVariable:
    @pytest.mark.parametrize(
        "var_name, var_value",
        [
            ("TEST_VAR", "test_value"),
            ("ANOTHER_TEST_VAR", "another_test_value"),
            ("YET_ANOTHER_TEST_VAR", "yet_another_test_value"),
        ],
    )
    def test_get_env_variable_success(
        self, monkeypatch: pytest.MonkeyPatch, var_name: str, var_value: str
    ) -> None:
        monkeypatch.setenv(var_name, var_value)
        assert get_env_variable(var_name) == var_value

    def test_get_env_variable_with_default(self) -> None:
        assert get_env_variable("NONEXISTENT_VAR", "default") == "default"

    def test_get_env_variable_raises_error(self) -> None:
        with pytest.raises(ValueError) as exc_info:
            get_env_variable("NONEXISTENT_VAR")
        assert "Environment variable NONEXISTENT_VAR is required but not set" in str(
            exc_info.value
        )


class TestStravaSecrets:
    def test_strava_secrets_loads_env_variables(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("STRAVA_CLIENT_ID", "test_strava_id")
        monkeypatch.setenv("STRAVA_SECRET_KEY", "test_strava_secret")

        secrets = StravaSecrets()
        assert secrets.strava_client_id == "test_strava_id"
        assert secrets.strava_secret_key == "test_strava_secret"


class TestSupabaseSecrets:
    def test_supabase_secrets_loads_env_variables(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_API_KEY", "test_api_key")
        monkeypatch.setenv("SUPABASE_TABLE", "test_table")

        secrets = SupabaseSecrets()
        assert secrets.supabase_url == "https://test.supabase.co"
        assert secrets.supabase_api_key == "test_api_key"
        assert secrets.supabase_table == "test_table"

    @pytest.mark.parametrize(
        "malformed_url, corrected_url",
        [
            ("https\\x3a//test.supabase.co", "https://test.supabase.co"),
            ("https\\x3a//another.supabase.co", "https://another.supabase.co"),
            ("https\\x3a//example.supabase.co", "https://example.supabase.co"),
        ],
    )
    def test_supabase_secrets_malformed_url_is_fixed(
        self,
        monkeypatch: pytest.MonkeyPatch,
        malformed_url: str,
        corrected_url: str,
    ) -> None:
        monkeypatch.setenv("SUPABASE_URL", malformed_url)
        monkeypatch.setenv("SUPABASE_API_KEY", "api_key")
        monkeypatch.setenv("SUPABASE_TABLE", "table")

        secrets = SupabaseSecrets()
        assert secrets.supabase_url == corrected_url

    def test_supabase_secrets_invalid_url_raises(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("SUPABASE_URL", "invalid_url")
        monkeypatch.setenv("SUPABASE_API_KEY", "key")
        monkeypatch.setenv("SUPABASE_TABLE", "table")

        with pytest.raises(ValueError, match="Invalid Supabase URL format"):
            SupabaseSecrets()

    def test_supabase_secrets_empty_api_key_raises(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("SUPABASE_URL", "https://valid.supabase.co")
        monkeypatch.setenv("SUPABASE_API_KEY", "")
        monkeypatch.setenv("SUPABASE_TABLE", "table")

        with pytest.raises(ValueError, match="Supabase API key cannot be empty"):
            SupabaseSecrets()


class TestFernetSecrets:
    def test_fernet_secrets_uses_env_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        key = Fernet.generate_key().decode()
        monkeypatch.setenv("FERNET_KEY", key)

        secrets = FernetSecrets()
        assert secrets.fernet_key == key
        assert isinstance(secrets.cipher, Fernet)

    def test_fernet_secrets_generates_key_if_not_set(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Asegúrate de que no está en el entorno
        monkeypatch.delenv("FERNET_KEY", raising=False)

        secrets = FernetSecrets()
        assert secrets.fernet_key is not None
        assert isinstance(secrets.cipher, Fernet)

        message = b"Hello, world!"
        encrypted = secrets.cipher.encrypt(message)
        decrypted = secrets.cipher.decrypt(encrypted)
        assert decrypted == message
