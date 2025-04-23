# from abc import ABC, abstractmethod
# from typing import Any, Dict
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict

from src.database.supabase_deleter import SupabaseDeleter
from src.strava_api.http.base_http_client import BaseHTTPClient

# class HTTPClient(ABC):
#     @abstractmethod
#     def get(
#         self, url: str, headers: Dict[str, str], params: Dict[str, Any] = None
#     ) -> Dict[str, Any]:
#         pass


# class BaseStravaAPI(ABC):
#     @abstractmethod
#     def __init__(self, access_token: str, http_client: HTTPClient, config: Any = None):
#         pass

#     @abstractmethod
#     def get_headers(self) -> Dict[str, str]:
#         pass

#     @abstractmethod
#     def get_url(self, endpoint: str) -> str:
#         pass


@dataclass
class StravaAPIConfig:
    base_url: str = "https://www.strava.com/api/v3"
    content_type: str = "application/json"


class BaseStravaAPI(ABC):
    def __init__(
        self,
        access_token: str,
        http_client: BaseHTTPClient,
        deleter: SupabaseDeleter = None,
        config: StravaAPIConfig = None,
    ):
        if not access_token:
            raise ValueError("\n\nAccess token must be provided.")
        self.access_token = access_token
        self.http_client = http_client
        self.config = config or StravaAPIConfig()
        self.deleter = deleter

    @abstractmethod
    def get_headers(self, access_token: str, content_type: str) -> Dict[str, str]: ...

    # @abstractmethod
    # def get_headers(self,access_token:str,content_type:str) -> Dict[str, str]:
    #     return {
    #         "Authorization": f"Bearer {self.access_token}",
    #         "Content-Type": self.config.content_type,
    #     }

    def get_url(self, endpoint: str) -> str:
        return f"{self.config.base_url}{endpoint}"
