from abc import ABC, abstractmethod

from src.utils import helpers as helper

from .strava_api import InterfaceStravaAPI


class InterfaceActivitiesStrava(ABC):
    def __init__(self, api: InterfaceStravaAPI, id_activity: int = None):
        self.api = api
        self.id_activity = id_activity
        self.logger = helper.Logger().setup_logger()

    @abstractmethod
    def fetch_activity_data(self, *args, **kwargs):
        pass
