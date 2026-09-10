from unittest.mock import AsyncMock, Mock, call

import pytest

from src.application.ports.activity_gateway import ActivityGateway
from src.application.ports.use_cases import ActivityQueries
from src.application.use_cases.streams import ActivityStreamService
from src.domain.activity_stream import StreamBatch
from tests.factories import activity_model, activity_stream


@pytest.fixture
def gateway() -> Mock:
    result = Mock(spec=ActivityGateway)
    result.get_activity_stream = AsyncMock()
    return result


@pytest.fixture
def activities() -> Mock:
    result = Mock(spec=ActivityQueries)
    result.get_activity_range = AsyncMock()
    return result


@pytest.fixture
def service(gateway: Mock, activities: Mock) -> ActivityStreamService:
    return ActivityStreamService(gateway, activities)


@pytest.mark.asyncio
async def test_gets_one_activity_stream(
    service: ActivityStreamService,
    gateway: Mock,
) -> None:
    stream = activity_stream(42)
    gateway.get_activity_stream.return_value = stream

    assert await service.get_streams_for_activity(42) is stream
    gateway.get_activity_stream.assert_awaited_once_with(42)


@pytest.mark.asyncio
async def test_rejects_invalid_activity_id(
    service: ActivityStreamService,
    gateway: Mock,
) -> None:
    with pytest.raises(ValueError, match="positive integer"):
        await service.get_streams_for_activity(0)

    gateway.get_activity_stream.assert_not_awaited()


@pytest.mark.asyncio
async def test_batch_retains_successes_and_failures(
    service: ActivityStreamService,
    gateway: Mock,
) -> None:
    gateway.get_activity_stream.side_effect = [
        activity_stream(1),
        TimeoutError("request timed out"),
    ]

    result = await service.get_streams_for_multiple_activities([1, 2])

    assert isinstance(result, StreamBatch)
    assert [stream.activity_id for stream in result.streams] == [1]
    assert result.failures[0].activity_id == 2
    assert result.failures[0].error_type == "TimeoutError"
    assert result.failures[0].message == "request timed out"


@pytest.mark.asyncio
async def test_batch_adds_message_for_empty_exception(
    service: ActivityStreamService,
    gateway: Mock,
) -> None:
    gateway.get_activity_stream.side_effect = RuntimeError()

    result = await service.get_streams_for_multiple_activities([1])

    assert result.failures[0].message == "Unknown stream fetch error"


@pytest.mark.asyncio
async def test_gets_streams_for_weekly_activity_ids(
    service: ActivityStreamService,
    gateway: Mock,
    activities: Mock,
) -> None:
    activities.get_activity_range.return_value = [activity_model(1), activity_model(2)]
    gateway.get_activity_stream.side_effect = [activity_stream(1), activity_stream(2)]

    result = await service.get_weekly_streams(previous_week=True)

    assert [stream.activity_id for stream in result.streams] == [1, 2]
    activities.get_activity_range.assert_awaited_once_with(previous_week=True)
    assert gateway.get_activity_stream.await_args_list == [call(1), call(2)]


@pytest.mark.asyncio
async def test_batch_validates_concurrency_limit(
    gateway: Mock,
    activities: Mock,
) -> None:
    service = ActivityStreamService(gateway, activities, max_concurrency=0)

    with pytest.raises(ValueError, match="at least one"):
        await service.get_streams_for_multiple_activities([1])
