from typing import Dict


class BaseStravaAPI:
    BASE_URL = "https://www.strava.com/api/v3"

    def __init__(self, access_token: str):
        if not access_token:
            raise ValueError("\n\nAccess token must be provided.")
        self.access_token = access_token

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    def _get_url(self, endpoint: str) -> str:
        return f"{self.BASE_URL}{endpoint}"
