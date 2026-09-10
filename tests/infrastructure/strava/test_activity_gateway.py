from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock

import pytest

from src.application.errors import InvalidExternalDataError
from src.domain.week_period import WeekPeriod, WeekSelection
from src.infrastructure.strava.activity_gateway import StravaActivityGateway
from tests.factories import activity_payload, stream_payload, zones_payload


@pytest.fixture
def api() -> Mock:
    result = Mock()
    result.make_request = AsyncMock()
    return result


@pytest.fixture
def period() -> WeekPeriod:
    return WeekPeriod.containing(
        datetime(2026, 9, 9, tzinfo=UTC),
        week=WeekSelection.CURRENT,
    )


@pytest.mark.asyncio
async def test_lists_activities_for_period(api: Mock, period: WeekPeriod) -> None:
    api.make_request.return_value = [activity_payload(1), activity_payload(2)]
    gateway = StravaActivityGateway(api)

    result = await gateway.list_activities(period)

    assert [activity.id for activity in result] == [1, 2]
    api.make_request.assert_awaited_once_with(
        endpoint="/athlete/activities",
        params={
            "per_page": 200,
            "page": 1,
            "after": period.start_epoch,
            "before": period.end_epoch,
        },
    )


@pytest.mark.asyncio
async def test_lists_every_activity_page(api: Mock, period: WeekPeriod) -> None:
    api.make_request.side_effect = [
        [activity_payload(1), activity_payload(2)],
        [activity_payload(3)],
    ]
    gateway = StravaActivityGateway(api, page_size=2)

    result = await gateway.list_activities(period)

    assert [activity.id for activity in result] == [1, 2, 3]
    assert api.make_request.await_args_list[1].kwargs["params"]["page"] == 2


@pytest.mark.parametrize("name", ["page_size", "max_pages"])
def test_rejects_non_positive_pagination_configuration(
    api: Mock,
    name: str,
) -> None:
    with pytest.raises(ValueError, match="at least one"):
        StravaActivityGateway(api, **{name: 0})


@pytest.mark.parametrize("name", ["page_size", "max_pages"])
def test_rejects_non_integer_pagination_configuration(
    api: Mock,
    name: str,
) -> None:
    with pytest.raises(TypeError, match="must be an integer"):
        StravaActivityGateway(api, **{name: True})


@pytest.mark.asyncio
async def test_stops_runaway_pagination(api: Mock, period: WeekPeriod) -> None:
    api.make_request.return_value = [activity_payload(1)]
    gateway = StravaActivityGateway(api, page_size=1, max_pages=2)

    with pytest.raises(InvalidExternalDataError, match="exceeded 2 pages"):
        await gateway.list_activities(period)

    assert api.make_request.await_count == 2


@pytest.mark.asyncio
async def test_translates_invalid_external_activity_data(
    api: Mock,
    period: WeekPeriod,
) -> None:
    api.make_request.return_value = [{"id": "not-an-integer"}]
    gateway = StravaActivityGateway(api)

    with pytest.raises(InvalidExternalDataError, match="activity list") as error:
        await gateway.list_activities(period)

    assert isinstance(error.value.__cause__, TypeError)


@pytest.mark.asyncio
async def test_gets_activity_details(api: Mock) -> None:
    api.make_request.return_value = activity_payload(7)
    gateway = StravaActivityGateway(api)

    result = await gateway.get_activity_details(7)

    assert result.id == 7
    api.make_request.assert_awaited_once_with("/activities/7")


@pytest.mark.asyncio
async def test_gets_activity_stream(api: Mock) -> None:
    api.make_request.return_value = stream_payload()
    gateway = StravaActivityGateway(api)

    result = await gateway.get_activity_stream(7)

    assert result.activity_id == 7
    api.make_request.assert_awaited_once_with(
        "/activities/7/streams",
        {"keys": "time,distance,heartrate", "key_by_type": "true"},
    )


@pytest.mark.asyncio
async def test_gets_activity_zones(api: Mock) -> None:
    api.make_request.return_value = zones_payload()
    gateway = StravaActivityGateway(api)

    result = await gateway.get_activity_zones(7)

    assert result.activity_id == 7
    api.make_request.assert_awaited_once_with("/activities/7/zones")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("method", "payload", "message"),
    [
        ("get_activity_details", {}, "activity data"),
        ("get_activity_stream", [], "activity stream data"),
        ("get_activity_zones", [], "heart-rate zone data"),
    ],
)
async def test_translates_invalid_detail_payloads(
    api: Mock,
    method: str,
    payload: object,
    message: str,
) -> None:
    api.make_request.return_value = payload
    gateway = StravaActivityGateway(api)

    with pytest.raises(InvalidExternalDataError, match=message):
        await getattr(gateway, method)(7)
