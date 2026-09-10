from typing import Protocol

from src.domain.activity_stream import ActivityStream
from src.domain.detailed_activity import DetailedActivity
from src.domain.heart_rate_zones import HeartRateZones
from src.domain.week_period import WeekPeriod


class ActivityGateway(Protocol):
    """Domain-oriented access to activities supplied by an external system."""

    async def list_activities(self, period: WeekPeriod) -> list[DetailedActivity]: ...

    async def get_activity_details(self, activity_id: int) -> DetailedActivity: ...

    async def get_activity_stream(self, activity_id: int) -> ActivityStream: ...

    async def get_activity_zones(self, activity_id: int) -> HeartRateZones: ...
