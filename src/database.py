from typing import Dict, Optional, Union

from supabase import Client

from src.interfaces.database import (
    DatabaseReaderInterface,
    DatabaseWriterInterface,
)
from src.interfaces.database import (
    T as type_T,
)
from src.utils import exception


class SupabaseReader(DatabaseReaderInterface):
    def __init__(self, client: Client):
        self.client = client

    def fetch_latest_record(
        self, table: str, column: str, order_by: Optional[str] = None
    ) -> Optional[type_T]:
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
