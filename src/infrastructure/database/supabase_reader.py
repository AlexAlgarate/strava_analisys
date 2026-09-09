from typing import cast

from supabase import Client

from src.interfaces.database.database_reader import IDatabaseReader
from src.utils import exceptions as exception


class SupabaseReader(IDatabaseReader):
    def __init__(self, client: Client) -> None:
        self.client = client

    def fetch_latest_record(
        self, table: str, column: str, order_by: str | None = None
    ) -> dict[str, str] | None:
        try:
            query = self.client.table(table).select(column)
            if order_by:
                query = query.order(order_by, desc=True)
            result = query.limit(1).execute()
            if not result or not result.data:
                return None

            # The Supabase SDK exposes rows as recursive JSON; this table stores
            # encrypted scalar strings only.
            return cast(dict[str, str], result.data[0])

        except Exception as e:
            raise exception.DatabaseOperationError(f"Failed to fetch data: {e}")
