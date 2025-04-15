from abc import ABC, abstractmethod

from src.utils.logging import Logger

from .strava_api import IHTTPClient


class IActivityFetcher(ABC):
    def __init__(
        self,
        api: IHTTPClient,
        id_activity: int = None,
    ):
        self.api = api
        self.id_activity = id_activity
        self.logger = Logger().setup_logger()

    @abstractmethod
    def fetch_activity_data(self, *args, **kwargs):
        pass
