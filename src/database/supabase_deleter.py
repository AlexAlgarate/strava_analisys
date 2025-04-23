import time
from typing import List

from supabase import Client

from src.interfaces.database_deleter import IDatabaseDeleter
from src.utils import exceptions as exception


class SupabaseDeleter(IDatabaseDeleter):
    def __init__(self, client: Client):
        self.client = client

    def delete_records(self, table: str, ids_to_delete: List[int]) -> bool:
        if not ids_to_delete:
            print("No records to delete.")
            return False

        try:
            result = (
                self.client.table(table)
                .delete()
                .in_("id", values=ids_to_delete)
                .execute()
            )
            print(f"Deleted {len(ids_to_delete)} records with IDs: {ids_to_delete}")
            return bool(result and result.data)

        except Exception as e:
            raise exception.DatabaseOperationError(f"Failed to delete data: {e}")

    def get_expired_token_ids(self, table: str, encryptor) -> List[int]:
        try:
            # Fetch all tokens with their expiration times
            result = self.client.table(table).select("id, expires_at").execute()
            if not result or not result.data:
                return []

            expired_ids = []
            for record in result.data:
                decrypted_data = encryptor.decrypt_data(record)
                if self._is_token_expired(decrypted_data["expires_at"]):
                    expired_ids.append(decrypted_data["id"])

            return sorted(expired_ids)

        except Exception as e:
            raise exception.DatabaseOperationError(
                f"Failed to fetch expired tokens: {e}"
            )

    def cleanup_expired_tokens(self, table: str, encryptor) -> bool:
        try:
            expired_ids = self.get_expired_token_ids(table, encryptor)
            if expired_ids:
                return self.delete_records(table, expired_ids)
            return False

        except Exception as e:
            raise exception.DatabaseOperationError(
                f"Failed to cleanup expired tokens: {e}"
            )

    @staticmethod
    def _is_token_expired(expires_at: str | int) -> bool:
        return int(time.time()) > int(expires_at)
