from collections.abc import Callable
from typing import Any
from unittest.mock import MagicMock

import pytest

from src.infrastructure.database.supabase_reader import SupabaseReader
from src.infrastructure.database.supabase_writer import SupabaseWriter
from src.utils import exceptions as exception


@pytest.fixture
def mock_client() -> MagicMock:
    return MagicMock()


@pytest.fixture
def supabase_reader(mock_client: MagicMock) -> SupabaseReader:
    return SupabaseReader(mock_client)


@pytest.fixture
def supabase_writer(mock_client: MagicMock) -> SupabaseWriter:
    return SupabaseWriter(mock_client)


@pytest.fixture
def mock_execute() -> Callable[..., MagicMock]:
    def _mock_execute(data: None = None, error: None = None) -> MagicMock:
        mock_exec = MagicMock()
        if error:
            mock_exec.execute.side_effect = Exception(error)
        else:
            mock_exec.execute.return_value.data = data
        return mock_exec

    return _mock_execute


class TestSupabaseReader:
    def mock_fetch_latest_record(
        self,
        supabase_reader: SupabaseReader,
        mock_execute: Callable[..., MagicMock],
        data: list[dict[str, Any]] | None = None,
        error: str | None = None,
    ) -> None:
        mock_query = MagicMock()
        mock_query.limit.return_value = mock_execute(data, error)
        supabase_reader.client = MagicMock()
        supabase_reader.client.table.return_value.select.return_value.order.return_value = mock_query

    def test_fetch_latest_record_success(
        self,
        supabase_reader: SupabaseReader,
        mock_execute: Callable[..., MagicMock],
    ) -> None:
        self.mock_fetch_latest_record(
            supabase_reader, mock_execute, data=[{"access_token": "test_token"}]
        )
        result = supabase_reader.fetch_latest_record(
            "test_table", "access_token", "expires_at"
        )
        assert result == {"access_token": "test_token"}

    def test_fetch_latest_record_no_data(
        self,
        supabase_reader: SupabaseReader,
        mock_execute: Callable[..., MagicMock],
    ) -> None:
        self.mock_fetch_latest_record(supabase_reader, mock_execute, data=[])
        result = supabase_reader.fetch_latest_record(
            "test_table", "access_token", "expires_at"
        )
        assert result is None

    def test_fetch_latest_record_exception(
        self, supabase_reader: SupabaseReader, mock_client: MagicMock
    ) -> None:
        mock_client.table.side_effect = Exception("Fetch error")
        with pytest.raises(
            exception.DatabaseOperationError,
            match="Failed to fetch data: Fetch error",
        ):
            supabase_reader.fetch_latest_record(
                "test_table", "access_token", "expires_at"
            )

    def test_fetch_latest_record_no_order_by(
        self,
        supabase_reader: SupabaseReader,
        mock_execute: Callable[..., MagicMock],
    ) -> None:
        mock_query = MagicMock()
        mock_query.limit.return_value.execute.return_value = MagicMock(
            data=[{"access_token": "test_token"}]
        )
        supabase_reader.client = MagicMock()
        supabase_reader.client.table.return_value.select.return_value = mock_query

        result = supabase_reader.fetch_latest_record("test_table", "access_token")
        assert result == {"access_token": "test_token"}

    def test_fetch_latest_record_empty_result(
        self,
        supabase_reader: SupabaseReader,
        mock_execute: Callable[..., MagicMock],
    ) -> None:
        self.mock_fetch_latest_record(supabase_reader, mock_execute, data=[])

        result = supabase_reader.fetch_latest_record(
            "test_table", "access_token", "expires_at"
        )
        assert result is None

    def test_fetch_latest_record_no_data_key(
        self,
        supabase_reader: SupabaseReader,
        mock_execute: Callable[..., MagicMock],
    ) -> None:
        self.mock_fetch_latest_record(supabase_reader, mock_execute, data=None)

        result = supabase_reader.fetch_latest_record(
            "test_table", "access_token", "expires_at"
        )
        assert result is None


class TestSupabaseWriter:
    def test_insert_record_success(
        self, supabase_writer: SupabaseWriter, mock_client: MagicMock
    ) -> None:
        mock_query = MagicMock()
        mock_query.execute.return_value.data = [{"id": 1}]
        mock_client.table.return_value.insert.return_value = mock_query

        result = supabase_writer.insert_record(
            "test_table", {"access_token": "test_token"}
        )
        assert result is True

    def test_insert_record_failure(
        self,
        supabase_writer: SupabaseWriter,
        mock_client: MagicMock,
        mock_execute: Callable[..., MagicMock],
    ) -> None:
        mock_client.table.return_value.insert.return_value = mock_execute(
            error="Insert error"
        )

        with pytest.raises(
            exception.DatabaseOperationError,
            match="Failed to insert data: Insert error",
        ):
            supabase_writer.insert_record("test_table", {"access_token": "test_token"})
