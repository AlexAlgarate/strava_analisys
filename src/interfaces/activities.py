from abc import ABC, abstractmethod

from src.utils import helpers as helper

from .strava_api import HTTPClient


class InterfaceActivitiesStrava(ABC):
    def __init__(
        self,
        api: HTTPClient,
        id_activity: int = None,
    ):
        self.api = api
        self.id_activity = id_activity
        self.logger = helper.Logger().setup_logger()

    @abstractmethod
    def fetch_activity_data(self, *args, **kwargs):
        pass


# class InterfaceActivitiesStrava(ABC):
#     def __init__(
#         self,
#         api: Union[SyncStravaAPI, AsyncStravaAPI],
#         id_activity: int = None,
#     ):
#         self.api = api
#         self.id_activity = id_activity
#         self.logger = helper.Logger().setup_logger()

#     @abstractmethod
#     def fetch_activity_data(self, *args, **kwargs):
#         pass
