from abc import ABC, abstractmethod

from src.strava_api.api.base_strava_api import BaseStravaAPI
from src.utils.logging import Logger


class IActivityFetcher(ABC):
    def __init__(
        self,
        api: BaseStravaAPI,
        id_activity: int = None,
    ):
        self.api = api
        self.id_activity = id_activity
        self.logger = Logger().setup_logger()

    @abstractmethod
    def fetch_activity_data(self, *args, **kwargs):
        pass
