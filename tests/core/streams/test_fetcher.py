import asyncio
from typing import cast
from unittest.mock import AsyncMock, Mock

import pytest

from src.core.streams.fetcher import ActivityStreamsFetcher
from src.domain.activity_stream import ActivityStream, StreamBatch
from src.utils import constants
from src.utils.exceptions import TooManyRequestError
from tests.factories import stream_payload


@pytest.fixture
def mock_async_api() -> Mock:
    api = Mock()
    api.make_request = AsyncMock()
    return api


@pytest.mark.asyncio
async def test_fetches_and_validates_one_activity_stream(mock_async_api: Mock) -> None:
    mock_async_api.make_request.return_value = stream_payload()

    result = await ActivityStreamsFetcher(
        api=mock_async_api,
        activity_id=123,
    ).fetch_activity_data(stream_keys=constants.ACTIVITY_STREAMS_KEYS)

    assert isinstance(result, ActivityStream)
    assert result.activity_id == 123
    assert len(result.samples) == 3
    mock_async_api.make_request.assert_awaited_once_with(
        "/activities/123/streams",
        {"keys": "time,distance,heartrate", "key_by_type": "true"},
    )


@pytest.mark.asyncio
async def test_rejects_non_object_stream_response(mock_async_api: Mock) -> None:
    mock_async_api.make_request.return_value = []

    with pytest.raises(TypeError, match="response must be an object"):
        await ActivityStreamsFetcher(
            api=mock_async_api,
            activity_id=123,
        ).fetch_activity_data(stream_keys=constants.ACTIVITY_STREAMS_KEYS)


@pytest.mark.parametrize("activity_id", [True, 0])
def test_rejects_invalid_activity_id(
    mock_async_api: Mock,
    activity_id: object,
) -> None:
    expected_error = TypeError if activity_id is True else ValueError
    with pytest.raises(expected_error):
        ActivityStreamsFetcher(
            api=mock_async_api,
            activity_id=cast(int, activity_id),
        )


@pytest.mark.asyncio
async def test_batch_retains_successes_and_failures(mock_async_api: Mock) -> None:
    mock_async_api.make_request.side_effect = [
        stream_payload(),
        TooManyRequestError("Rate limit exceeded"),
    ]

    result = await ActivityStreamsFetcher.fetch_multiple_activities_streams(
        api=mock_async_api,
        list_id_activities=[1, 2],
        stream_keys=constants.ACTIVITY_STREAMS_KEYS,
    )

    assert isinstance(result, StreamBatch)
    assert result.sample_count == 3
    assert result.is_partial
    assert [stream.activity_id for stream in result.streams] == [1]
    assert result.failures[0].activity_id == 2
    assert result.failures[0].error_type == "TooManyRequestError"
    assert result.failures[0].message == "Rate limit exceeded"


@pytest.mark.asyncio
async def test_batch_limits_concurrent_requests(mock_async_api: Mock) -> None:
    active_requests = 0
    peak_requests = 0

    async def delayed_response(*_args: object, **_kwargs: object) -> object:
        nonlocal active_requests, peak_requests
        active_requests += 1
        peak_requests = max(peak_requests, active_requests)
        await asyncio.sleep(0)
        active_requests -= 1
        return stream_payload()

    mock_async_api.make_request.side_effect = delayed_response

    result = await ActivityStreamsFetcher.fetch_multiple_activities_streams(
        api=mock_async_api,
        list_id_activities=[1, 2, 3, 4],
        stream_keys=constants.ACTIVITY_STREAMS_KEYS,
        max_concurrency=2,
    )

    assert len(result.streams) == 4
    assert peak_requests == 2


@pytest.mark.asyncio
async def test_batch_rejects_invalid_concurrency(mock_async_api: Mock) -> None:
    with pytest.raises(ValueError, match="at least one"):
        await ActivityStreamsFetcher.fetch_multiple_activities_streams(
            api=mock_async_api,
            list_id_activities=[1],
            stream_keys=constants.ACTIVITY_STREAMS_KEYS,
            max_concurrency=0,
        )
