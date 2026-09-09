from datetime import timedelta

import pytest

from src.domain.activity_summary import WeeklyActivitySummary
from src.presentation.console_output.weekly_summary_presenter import (
    ConsoleSummaryPresenter,
)


def test_presents_summary_and_marks_unknown_averages(
    capsys: pytest.CaptureFixture[str],
) -> None:
    summary = WeeklyActivitySummary(
        activity_count=0,
        total_distance_km=0,
        total_moving_time=timedelta(),
        total_elevation_gain=0,
        average_heartrate=None,
        average_max_heartrate=None,
        total_calories=0,
        average_perceived_exertion=None,
    )

    ConsoleSummaryPresenter().present_weekly_report(summary)

    output = capsys.readouterr().out
    assert "Activities: 0" in output
    assert "Average Heart Rate: N/A" in output
    assert "Average Perceived Exertion: N/A" in output
