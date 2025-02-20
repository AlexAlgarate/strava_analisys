from typing import Generator
from unittest.mock import MagicMock, patch

import pytest

from src.database import SupabaseClient
from src.utils import exception


class TestSupabaseClient:
    @pytest.fixture
    def supabase_client(self) -> Generator[SupabaseClient, None, None]:
        with patch("src.database.create_client") as mock_create_client:
            mock_client = MagicMock()
            mock_create_client.return_value = mock_client
            client = SupabaseClient("https://test.supabase.co", "test_supabase_key")
            client.client = mock_client
            yield client

    @pytest.fixture
    def mock_execute(self):
        def _mock_execute(data=None, error=None):
            mock_exec = MagicMock()
            if error:
                mock_exec.execute.side_effect = Exception(error)
            else:
                mock_exec.execute.return_value.data = data
            return mock_exec

        return _mock_execute

    def mock_fetch_latest_record(
        self,
        supabase_client,
        mock_execute,
        data=None,
        error=None,
    ):
        supabase_client.client.table.return_value.select.return_value.order.return_value.limit.return_value = mock_execute(
            data, error
        )

    def test_fetch_latest_record_success(self, supabase_client, mock_execute):
        self.mock_fetch_latest_record(
            supabase_client,
            mock_execute,
            data=[{"access_token": "test_token"}],
        )

        result = supabase_client.fetch_latest_record(
            "test_table", "access_token", "expires_at"
        )
        assert result == {"access_token": "test_token"}

    def test_fetch_latest_record_failure(self, supabase_client, mock_execute):
        self.mock_fetch_latest_record(
            supabase_client,
            mock_execute,
            error="Fetch error",
        )

        with pytest.raises(
            exception.DatabaseOperationError, match="Failed to fetch data: Fetch error"
        ):
            supabase_client.fetch_latest_record(
                "test_table", "access_token", "expires_at"
            )

    def test_fetch_latest_record_no_order_by(self, supabase_client, mock_execute):
        mock_query = MagicMock()
        mock_query.limit.return_value.execute.return_value = MagicMock(
            data=[{"access_token": "test_token"}]
        )
        supabase_client.client.table.return_value.select.return_value = mock_query

        result = supabase_client.fetch_latest_record("test_table", "access_token")
        assert result == {"access_token": "test_token"}

    def test_fetch_latest_record_empty_result(self, supabase_client, mock_execute):
        self.mock_fetch_latest_record(supabase_client, mock_execute, data=[])

        result = supabase_client.fetch_latest_record(
            "test_table", "access_token", "expires_at"
        )
        assert result is None

    def test_fetch_latest_record_no_data_key(self, supabase_client, mock_execute):
        self.mock_fetch_latest_record(supabase_client, mock_execute, data=None)

        result = supabase_client.fetch_latest_record(
            "test_table", "access_token", "expires_at"
        )
        assert result is None

    def test_insert_record_success(self, supabase_client, mock_execute):
        mock_query = mock_execute(data=[{"id": 1}])
        supabase_client.client.table.return_value.insert.return_value = mock_query

        result = supabase_client.insert_record(
            "test_table", {"access_token": "test_token"}
        )
        assert result is True

    def test_insert_record_failure(self, supabase_client, mock_execute):
        supabase_client.client.table.return_value.insert.return_value = mock_execute(
            error="Insert error"
        )

        with pytest.raises(
            exception.DatabaseOperationError,
            match="Failed to insert data: Insert error",
        ):
            supabase_client.insert_record("test_table", {"access_token": "test_token"})
