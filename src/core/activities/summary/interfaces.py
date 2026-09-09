from abc import ABC, abstractmethod
from typing import Any


class IMetricCalculator(ABC):
    @abstractmethod
    def calculate(self, activities: list[dict[str, Any]]) -> dict[str, Any]:
        pass


class IActivitySummaryBuilder(ABC):
    @abstractmethod
    def reset(self) -> None:
        pass

    @abstractmethod
    def add_distance(self, value: float) -> None:
        pass

    @abstractmethod
    def add_moving_time(self, value: str) -> None:
        pass

    @abstractmethod
    def add_elevation_gain(self, value: float) -> None:
        pass

    @abstractmethod
    def add_heart_rate_metrics(self, avg: float, max_avg: float) -> None:
        pass

    @abstractmethod
    def add_calories(self, value: float) -> None:
        pass

    @abstractmethod
    def add_perceived_exertion(self, value: float) -> None:
        pass

    @abstractmethod
    def get_summary(self) -> dict[str, Any]:
        pass


class IActivityDataLoader(ABC):
    @abstractmethod
    def load_activities(self) -> list[dict[str, Any]]:
        pass


class IActivitySummaryPresenter(ABC):
    @abstractmethod
    def present_weekly_report(self, summary: dict[str, Any]) -> None:
        pass
