import time
from typing import cast

from supabase import Client

from src.interfaces.database.database_deleter import IDatabaseDeleter
from src.interfaces.encryption.encryptor import IEncryptation
from src.utils import exceptions as exception


class SupabaseDeleter(IDatabaseDeleter):
    def __init__(self, client: Client) -> None:
        self.client = client

    def delete_records(self, table: str, ids_to_delete: list[int]) -> bool:
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

    def get_expired_token_ids(self, table: str, encryptor: IEncryptation) -> list[int]:
        try:
            # Fetch all tokens with their expiration times
            result = self.client.table(table).select("id, expires_at").execute()
            if not result or not result.data:
                return []

            expired_ids: list[int] = []
            for record in result.data:
                # The token table contains encrypted string values, while the
                # Supabase SDK exposes each row as recursive JSON.
                encrypted_record = cast(dict[str, str], record)
                decrypted_data = encryptor.decrypt_data(encrypted_record)
                if self._is_token_expired(decrypted_data["expires_at"]):
                    expired_ids.append(int(decrypted_data["id"]))

            return sorted(expired_ids)

        except Exception as e:
            raise exception.DatabaseOperationError(
                f"Failed to fetch expired tokens: {e}"
            )

    def cleanup_expired_tokens(self, table: str, encryptor: IEncryptation) -> bool:
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
