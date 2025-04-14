from typing import Dict

from supabase import Client

from src.interfaces.database import DatabaseWriterInterface
from src.utils import exceptions as exception


class SupabaseWriter(DatabaseWriterInterface):
    def __init__(self, client: Client):
        self.client = client

    def insert_record(self, table: str, data: Dict[str, str | int]) -> bool:
        try:
            result = self.client.table(table).insert(data).execute()
            return bool(result and result.data)

        except Exception as e:
            raise exception.DatabaseOperationError(f"Failed to insert data: {e}")
