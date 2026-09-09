from src.core.activities.summary.ports import SummaryData


class ConsoleSummaryPresenter:
    """Render a weekly activity summary in the terminal."""

    def present_weekly_report(self, summary: SummaryData) -> None:
        print("\n---- Weekly Summary ----")
        print(f"Total Distance: {summary['total_distance']} km")
        print(f"Total Moving Time: {summary['total_moving_time']}")
        print(f"Total Elevation Gain: {summary['total_elevation_gain']} m")
        print(f"Average Heart Rate: {summary['avg_heartrate']} bpm")
        print(f"Average Max Heart Rate: {summary['avg_max_heartrate']} bpm")
        print(f"Total Calories: {summary['total_calories']} kcal")
        print(f"Average Perceived Exertion: {summary['avg_perceived_exertion']}")
