from datetime import UTC, datetime, timedelta, timezone
from typing import cast

import pytest

from src.domain.week_period import WeekPeriod, WeekSelection


def test_builds_current_utc_week() -> None:
    instant = datetime(2026, 9, 9, 15, 30, tzinfo=UTC)

    period = WeekPeriod.containing(instant, week=WeekSelection.CURRENT)

    assert period.start == datetime(2026, 9, 7, tzinfo=UTC)
    assert period.end == datetime(2026, 9, 14, tzinfo=UTC)
    assert period.end - period.start == timedelta(weeks=1)


def test_builds_previous_week_and_normalizes_timezone() -> None:
    madrid_summer = timezone(timedelta(hours=2))
    instant = datetime(2026, 9, 9, 17, 30, tzinfo=madrid_summer)

    period = WeekPeriod.containing(instant, week=WeekSelection.PREVIOUS)

    assert period.start == datetime(2026, 8, 31, tzinfo=UTC)
    assert period.end == datetime(2026, 9, 7, tzinfo=UTC)


def test_exposes_epoch_boundaries() -> None:
    period = WeekPeriod(
        start=datetime(1970, 1, 5, tzinfo=UTC),
        end=datetime(1970, 1, 12, tzinfo=UTC),
    )

    assert period.start_epoch == 345_600
    assert period.end_epoch == 950_400


@pytest.mark.parametrize(
    ("start", "end", "error_type", "message"),
    [
        (
            datetime(2026, 9, 7),  # noqa: DTZ001 - deliberately invalid input
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
        (
            datetime(2026, 9, 7, tzinfo=timezone(timedelta(hours=1))),
            datetime(2026, 9, 14, tzinfo=timezone(timedelta(hours=1))),
            ValueError,
            "in UTC",
        ),
        (
            datetime(2026, 9, 8, tzinfo=UTC),
            datetime(2026, 9, 15, tzinfo=UTC),
            ValueError,
            "start on Monday",
        ),
        (
            datetime(2026, 9, 7, tzinfo=UTC),
            datetime(2026, 9, 13, tzinfo=UTC),
            ValueError,
            "exactly seven days",
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
        WeekPeriod.containing(
            datetime(2026, 9, 9),  # noqa: DTZ001 - deliberately invalid input
            week=WeekSelection.CURRENT,
        )

    with pytest.raises(TypeError, match="must be a datetime"):
        WeekPeriod.containing(
            cast(datetime, _unknown("2026-09-09")),
            week=WeekSelection.CURRENT,
        )


def test_rejects_invalid_week_selection() -> None:
    with pytest.raises(TypeError, match="must be a WeekSelection"):
        WeekPeriod.containing(
            datetime(2026, 9, 9, tzinfo=UTC),
            week=cast(WeekSelection, _unknown(True)),
        )


def _unknown(value: object) -> object:
    return value
