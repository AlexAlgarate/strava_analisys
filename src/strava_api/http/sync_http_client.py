from typing import Any, Dict

import requests

from src.utils import exceptions

from ...interfaces.sync_http_client import BaseSyncHTTPClient


class SyncHTTPClient(BaseSyncHTTPClient):
    def get_method(
        self, url: str, headers: Dict[str, str], params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            if response.status_code == 401:
                raise exceptions.UnauthorizedError(
                    "\n\nUnauthorized. Check your token."
                )
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"\n\nError making request to {url}: {e}")
            print("Deleting token from Supabase.")
            return {}
