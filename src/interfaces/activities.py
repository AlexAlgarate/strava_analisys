from abc import ABC, abstractmethod

from .strava_api import BaseStravaAPI


class IActivityFetcher(ABC):
    def __init__(
        self,
        api: BaseStravaAPI,
        id_activity: int = None,
    ):
        self.api = api
        self.id_activity = id_activity

    @abstractmethod
    def fetch_activity_data(self, *args, **kwargs):
        pass
