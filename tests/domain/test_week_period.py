from datetime import UTC, datetime, timedelta, timezone
from typing import cast

import pytest

from src.domain.week_period import WeekPeriod


def test_builds_current_utc_week() -> None:
    instant = datetime(2026, 9, 9, 15, 30, tzinfo=UTC)

    period = WeekPeriod.containing(instant)

    assert period.start == datetime(2026, 9, 7, tzinfo=UTC)
    assert period.end == datetime(2026, 9, 14, tzinfo=UTC)
    assert period.end - period.start == timedelta(weeks=1)


def test_builds_previous_week_and_normalizes_timezone() -> None:
    madrid_summer = timezone(timedelta(hours=2))
    instant = datetime(2026, 9, 9, 17, 30, tzinfo=madrid_summer)

    period = WeekPeriod.containing(instant, previous_week=True)

    assert period.start == datetime(2026, 8, 31, tzinfo=UTC)
    assert period.end == datetime(2026, 9, 7, tzinfo=UTC)


def test_exposes_epoch_boundaries() -> None:
    period = WeekPeriod(
        start=datetime(1970, 1, 1, tzinfo=UTC),
        end=datetime(1970, 1, 8, tzinfo=UTC),
    )

    assert period.start_epoch == 0
    assert period.end_epoch == 604_800


@pytest.mark.parametrize(
    ("start", "end", "error_type", "message"),
    [
        (
            datetime(2026, 9, 7),
            datetime(2026, 9, 14, tzinfo=UTC),
            ValueError,
            "timezone-aware",
        ),
        (
            datetime(2026, 9, 14, tzinfo=UTC),
            datetime(2026, 9, 7, tzinfo=UTC),
            ValueError,
            "later",
        ),
    ],
)
def test_rejects_invalid_periods(
    start: datetime,
    end: datetime,
    error_type: type[Exception],
    message: str,
) -> None:
    with pytest.raises(error_type, match=message):
        WeekPeriod(start=start, end=end)


def test_rejects_invalid_reference_instant() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        WeekPeriod.containing(datetime(2026, 9, 9))

    with pytest.raises(TypeError, match="must be a datetime"):
        WeekPeriod.containing(cast(datetime, "2026-09-09"))
