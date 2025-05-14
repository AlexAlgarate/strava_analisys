from typing import Dict

from supabase import Client

from src.interfaces.database.database_writer import IDatabaseWriter
from src.utils import exceptions as exception


class SupabaseWriter(IDatabaseWriter):
    def __init__(self, client: Client):
        self.client = client

    def insert_record(self, table: str, data: Dict[str, str]) -> bool:
        try:
            result = self.client.table(table).insert(data).execute()
            return bool(result and result.data)

        except Exception as e:
            raise exception.DatabaseOperationError(f"Failed to insert data: {e}")
