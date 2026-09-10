from collections.abc import Callable
from datetime import UTC, datetime

from src.application.concurrency import DEFAULT_MAX_CONCURRENCY, map_concurrently
from src.application.errors import ActivitiesNotFoundError
from src.application.ports.activity_gateway import ActivityGateway
from src.domain.detailed_activity import DetailedActivity
from src.domain.week_period import WeekPeriod

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
        self._max_concurrency = max_concurrency

    async def get_activity_range(
        self,
        previous_week: bool = False,
    ) -> list[DetailedActivity]:
        """Return all activities in the current or previous UTC week."""
        period = WeekPeriod.containing(
            self._clock(),
            previous_week=previous_week,
        )
        return await self._gateway.list_activities(period)

    async def get_activity_details(
        self,
        previous_week: bool = False,
    ) -> list[DetailedActivity]:
        """Return full details for every activity in the selected week."""
        activities = await self.get_activity_range(previous_week=previous_week)
        if not activities:
            raise ActivitiesNotFoundError("No activities found.")

        return await map_concurrently(
            [activity.id for activity in activities],
            self._gateway.get_activity_details,
            max_concurrency=self._max_concurrency,
        )
