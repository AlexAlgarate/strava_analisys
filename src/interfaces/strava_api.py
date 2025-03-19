from abc import ABC, abstractmethod


class SyncStravaAPI(ABC):
    @abstractmethod
    def make_request(self, endpoint: str, params: dict = None) -> dict:
        pass


class AsyncStravaAPI(ABC):
    @abstractmethod
    async def make_request_async(
        self,
        endpoint: str,
        params: dict = None,
        *args,
    ) -> dict:
        pass
