from collections.abc import Sequence

from src.application.concurrency import (
    DEFAULT_MAX_CONCURRENCY,
    map_concurrently,
    require_concurrency_limit,
)
from src.application.errors import ExternalServiceError
from src.application.ports.activity_gateway import ActivityStreamGateway
from src.application.ports.use_cases import WeeklyActivityList
from src.domain.activity_id import require_activity_id
from src.domain.activity_stream import (
    ActivityStream,
    StreamBatch,
    StreamFetchFailure,
)
from src.domain.week_period import WeekSelection


class ActivityStreamService:
    """Retrieve individual or batched activity streams."""

    def __init__(
        self,
        gateway: ActivityStreamGateway,
        activities: WeeklyActivityList,
        *,
        max_concurrency: int = DEFAULT_MAX_CONCURRENCY,
    ) -> None:
        self._gateway = gateway
        self._activities = activities
        self._max_concurrency = require_concurrency_limit(max_concurrency)

    async def get_streams_for_activity(self, activity_id: int) -> ActivityStream:
        return await self._gateway.get_activity_stream(require_activity_id(activity_id))

    async def get_streams_for_multiple_activities(
        self,
        activity_ids: Sequence[int],
    ) -> StreamBatch:
        validated_ids = tuple(require_activity_id(value) for value in activity_ids)
        if len(validated_ids) != len(set(validated_ids)):
            raise ValueError("Activity IDs in a stream batch must be unique.")

        results = await map_concurrently(
            validated_ids,
            self._fetch_one,
            max_concurrency=self._max_concurrency,
        )
        return _to_stream_batch(results)

    async def get_weekly_streams(
        self,
        *,
        week: WeekSelection,
    ) -> StreamBatch:
        activities = await self._activities.list_activities(week=week)
        return await self.get_streams_for_multiple_activities(
            [activity.id for activity in activities]
        )

    async def _fetch_one(
        self,
        activity_id: int,
    ) -> ActivityStream | StreamFetchFailure:
        try:
            return await self.get_streams_for_activity(activity_id)
        except ExternalServiceError as error:
            message = str(error).strip() or "Unknown stream fetch error"
            return StreamFetchFailure(
                activity_id=activity_id,
                error_type=type(error).__name__,
                message=message,
            )


def _to_stream_batch(results: Sequence[object]) -> StreamBatch:
    streams: list[ActivityStream] = []
    failures: list[StreamFetchFailure] = []
    for result in results:
        if isinstance(result, ActivityStream):
            streams.append(result)
        elif isinstance(result, StreamFetchFailure):
            failures.append(result)
        else:
            raise TypeError(
                "Stream retrieval returned neither an ActivityStream nor a "
                "StreamFetchFailure."
            )
    return StreamBatch(streams=tuple(streams), failures=tuple(failures))
