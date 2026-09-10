from unittest.mock import AsyncMock, Mock, call

import pytest

from src.application.errors import ExternalServiceError
from src.application.ports.activity_gateway import ActivityStreamGateway
from src.application.ports.use_cases import WeeklyActivityList
from src.application.use_cases.streams import ActivityStreamService
from src.domain.activity_stream import StreamBatch
from src.domain.week_period import WeekSelection
from tests.factories import activity_model, activity_stream


@pytest.fixture
def gateway() -> Mock:
    result = Mock(spec=ActivityStreamGateway)
    result.get_activity_stream = AsyncMock()
    return result


@pytest.fixture
def activities() -> Mock:
    result = Mock(spec=WeeklyActivityList)
    result.list_activities = AsyncMock()
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
        ExternalServiceError("request timed out"),
    ]

    result = await service.get_streams_for_multiple_activities([1, 2])

    assert isinstance(result, StreamBatch)
    assert [stream.activity_id for stream in result.streams] == [1]
    assert result.failures[0].activity_id == 2
    assert result.failures[0].error_type == "ExternalServiceError"
    assert result.failures[0].message == "request timed out"


@pytest.mark.asyncio
@pytest.mark.parametrize("message", ["", "   ", "\t"])
async def test_batch_adds_message_for_exception_without_meaningful_text(
    service: ActivityStreamService,
    gateway: Mock,
    message: str,
) -> None:
    gateway.get_activity_stream.side_effect = ExternalServiceError(message)

    result = await service.get_streams_for_multiple_activities([1])

    assert result.failures[0].message == "Unknown stream fetch error"


@pytest.mark.asyncio
async def test_batch_rejects_invalid_ids_before_calling_gateway(
    service: ActivityStreamService,
    gateway: Mock,
) -> None:
    with pytest.raises(ValueError, match="positive integer"):
        await service.get_streams_for_multiple_activities([1, 0])

    gateway.get_activity_stream.assert_not_awaited()


@pytest.mark.asyncio
async def test_batch_rejects_duplicate_ids_before_calling_gateway(
    service: ActivityStreamService,
    gateway: Mock,
) -> None:
    with pytest.raises(ValueError, match="must be unique"):
        await service.get_streams_for_multiple_activities([1, 1])

    gateway.get_activity_stream.assert_not_awaited()


@pytest.mark.asyncio
async def test_batch_does_not_hide_programming_errors(
    service: ActivityStreamService,
    gateway: Mock,
) -> None:
    gateway.get_activity_stream.side_effect = AttributeError("implementation bug")

    with pytest.raises(AttributeError, match="implementation bug"):
        await service.get_streams_for_multiple_activities([1])


@pytest.mark.asyncio
async def test_batch_rejects_a_gateway_result_outside_its_contract(
    service: ActivityStreamService,
    gateway: Mock,
) -> None:
    gateway.get_activity_stream.return_value = None

    with pytest.raises(TypeError, match="neither an ActivityStream"):
        await service.get_streams_for_multiple_activities([1])


@pytest.mark.asyncio
async def test_gets_streams_for_weekly_activity_ids(
    service: ActivityStreamService,
    gateway: Mock,
    activities: Mock,
) -> None:
    activities.list_activities.return_value = [activity_model(1), activity_model(2)]
    gateway.get_activity_stream.side_effect = [activity_stream(1), activity_stream(2)]

    result = await service.get_weekly_streams(week=WeekSelection.PREVIOUS)

    assert [stream.activity_id for stream in result.streams] == [1, 2]
    activities.list_activities.assert_awaited_once_with(week=WeekSelection.PREVIOUS)
    assert gateway.get_activity_stream.await_args_list == [call(1), call(2)]


def test_service_rejects_invalid_concurrency_limit(
    gateway: Mock,
    activities: Mock,
) -> None:
    with pytest.raises(ValueError, match="at least one"):
        ActivityStreamService(gateway, activities, max_concurrency=0)
