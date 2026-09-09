from src.domain.activity_summary import WeeklyActivitySummary


class ConsoleSummaryPresenter:
    """Render a weekly activity summary in the terminal."""

    def present_weekly_report(self, summary: WeeklyActivitySummary) -> None:
        print("\n---- Weekly Summary ----")
        print(f"Activities: {summary.activity_count}")
        print(f"Total Distance: {summary.total_distance_km} km")
        print(f"Total Moving Time: {summary.total_moving_time}")
        print(f"Total Elevation Gain: {summary.total_elevation_gain} m")
        print(
            f"Average Heart Rate: {_format_optional(summary.average_heartrate, 'bpm')}"
        )
        print(
            "Average Max Heart Rate: "
            f"{_format_optional(summary.average_max_heartrate, 'bpm')}"
        )
        print(f"Total Calories: {summary.total_calories} kcal")
        print(
            "Average Perceived Exertion: "
            f"{_format_optional(summary.average_perceived_exertion)}"
        )


def _format_optional(value: float | None, unit: str = "") -> str:
    if value is None:
        return "N/A"
    suffix = f" {unit}" if unit else ""
    return f"{value}{suffix}"
