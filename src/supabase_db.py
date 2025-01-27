from typing import Dict, Optional, Union

from supabase import create_client


class SupabaseClient:
    def __init__(self, url: str, api_key: str):
        self.client = create_client(url, api_key)

    def fetch_latest_record(
        self, table: str, column: str, order_by: Optional[str] = None
    ) -> Optional[Dict[str, Union[str, int]]]:
        try:
            query = (
                self.client.table(table)
                .select(column)
                .order(order_by, desc=True)
                .limit(1)
                .execute()
            )
            return query.data[0] if query and query.data else None
        except Exception as e:
            print(f"Error fetching data: {e}")
            return None

    def insert_record(self, table: str, data: Dict[str, Union[str, int]]) -> bool:
        try:
            self.client.table(table).insert(data).execute()
            print("Data successfully inserted.")
            return True

        except Exception as e:
            print(f"Error inserting data into Supabase: {e}")
            return False
