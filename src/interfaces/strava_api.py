from abc import ABC, abstractmethod


class InterfaceStravaAPI(ABC):
    @abstractmethod
    def make_request(self, endpoint: str, params: dict = None) -> dict:
        pass

    @abstractmethod
    async def make_request_async(self, endpoint: str, params: dict = None) -> dict:
        pass
