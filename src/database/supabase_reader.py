from supabase import Client

from src.interfaces.database import IDatabaseReader
from src.interfaces.database import T as type_T
from src.utils import exceptions as exception


class SupabaseReader(IDatabaseReader):
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
