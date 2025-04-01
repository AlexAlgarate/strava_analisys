from typing import Dict, List, Union

from supabase import Client

from src.interfaces.database import (
    DatabaseDeleterInterface,
    DatabaseReaderInterface,
    DatabaseWriterInterface,
)
from src.interfaces.database import (
    T as type_T,
)
from src.utils import exceptions as exception


class SupabaseReader(DatabaseReaderInterface):
    def __init__(self, client: Client):
        self.client = client

    def fetch_latest_record(
        self, table: str, column: str, order_by: str | None = None
    ) -> type_T | None:
        try:
            query = self.client.table(table).select(column)
            if order_by:
                query = query.order(order_by, desc=True)
            result = query.limit(1).execute()
            return result.data[0] if result and result.data else None

        except Exception as e:
            raise exception.DatabaseOperationError(f"Failed to fetch data: {e}")


class SupabaseWriter(DatabaseWriterInterface):
    def __init__(self, client: Client):
        self.client = client

    def insert_record(self, table: str, data: Dict[str, Union[str, int]]) -> bool:
        try:
            result = self.client.table(table).insert(data).execute()
            return bool(result and result.data)

        except Exception as e:
            raise exception.DatabaseOperationError(f"Failed to insert data: {e}")


class SupabaseDeleter(DatabaseDeleterInterface):
    def __init__(self, client: Client):
        self.client = client

    def delete_record(self, table: str, column: str, record: List[int]) -> bool:
        try:
            result = (
                self.client.table(table)
                .delete()
                .in_(column=column, values=record)
                .execute()
            )
            return bool(result and result.data)

        except Exception as e:
            raise exception.DatabaseOperationError(f"Failed to delete data: {e}")
