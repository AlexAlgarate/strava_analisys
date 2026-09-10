from collections.abc import Callable
from datetime import UTC, datetime

from src.application.concurrency import (
    DEFAULT_MAX_CONCURRENCY,
    map_concurrently,
    require_concurrency_limit,
)
from src.application.ports.activity_gateway import ActivityGateway
from src.domain.detailed_activity import DetailedActivity
from src.domain.week_period import WeekPeriod, WeekSelection

type Clock = Callable[[], datetime]


def utc_now() -> datetime:
    """Return the current instant in UTC."""
    return datetime.now(UTC)


class ActivityService:
    """Run weekly activity queries independently of the external provider."""

    def __init__(
        self,
        gateway: ActivityGateway,
        *,
        clock: Clock = utc_now,
        max_concurrency: int = DEFAULT_MAX_CONCURRENCY,
    ) -> None:
        self._gateway = gateway
        self._clock = clock
        self._max_concurrency = require_concurrency_limit(max_concurrency)

    async def get_activity_range(
        self,
        *,
        week: WeekSelection,
    ) -> list[DetailedActivity]:
        """Return all activities in the selected UTC week."""
        period = WeekPeriod.containing(
            self._clock(),
            week=week,
        )
        return await self._gateway.list_activities(period)

    async def get_activity_details(
        self,
        *,
        week: WeekSelection,
    ) -> list[DetailedActivity]:
        """Return full details for every activity in the selected week."""
        activities = await self.get_activity_range(week=week)
        return await map_concurrently(
            [activity.id for activity in activities],
            self._gateway.get_activity_details,
            max_concurrency=self._max_concurrency,
        )
