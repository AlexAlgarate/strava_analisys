from collections.abc import Sequence

from src.application.concurrency import DEFAULT_MAX_CONCURRENCY, map_concurrently
from src.application.ports.activity_gateway import ActivityGateway
from src.application.ports.use_cases import ActivityQueries
from src.domain.activity_id import require_activity_id
from src.domain.activity_stream import (
    ActivityStream,
    StreamBatch,
    StreamFetchFailure,
)


class ActivityStreamService:
    """Retrieve individual or batched activity streams."""

    def __init__(
        self,
        gateway: ActivityGateway,
        activities: ActivityQueries,
        *,
        max_concurrency: int = DEFAULT_MAX_CONCURRENCY,
    ) -> None:
        self._gateway = gateway
        self._activities = activities
        self._max_concurrency = max_concurrency

    async def get_streams_for_activity(self, activity_id: int) -> ActivityStream:
        return await self._gateway.get_activity_stream(
            require_activity_id(activity_id)
        )

    async def get_streams_for_multiple_activities(
        self,
        activity_ids: Sequence[int],
    ) -> StreamBatch:
        results = await map_concurrently(
            activity_ids,
            self._fetch_one,
            max_concurrency=self._max_concurrency,
        )
        return StreamBatch(
            streams=tuple(
                result for result in results if isinstance(result, ActivityStream)
            ),
            failures=tuple(
                result for result in results if isinstance(result, StreamFetchFailure)
            ),
        )

    async def get_weekly_streams(
        self,
        previous_week: bool = False,
    ) -> StreamBatch:
        activities = await self._activities.get_activity_range(
            previous_week=previous_week
        )
        return await self.get_streams_for_multiple_activities(
            [activity.id for activity in activities]
        )

    async def _fetch_one(
        self,
        activity_id: int,
    ) -> ActivityStream | StreamFetchFailure:
        try:
            return await self.get_streams_for_activity(activity_id)
        except Exception as error:  # noqa: BLE001 - batch boundary records failures
            return StreamFetchFailure(
                activity_id=activity_id,
                error_type=type(error).__name__,
                message=str(error) or "Unknown stream fetch error",
            )
