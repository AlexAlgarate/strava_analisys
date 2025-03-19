from abc import ABC, abstractmethod
from typing import Union

from src.utils import helpers as helper

from .strava_api import AsyncStravaAPI, SyncStravaAPI


class InterfaceActivitiesStrava(ABC):
    def __init__(
        self,
        api: Union[SyncStravaAPI, AsyncStravaAPI],
        id_activity: int = None,
    ):
        self.api = api
        self.id_activity = id_activity
        self.logger = helper.Logger().setup_logger()

    @abstractmethod
    def fetch_activity_data(self, *args, **kwargs):
        pass
