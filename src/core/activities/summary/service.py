from src.core.activities.summary.calculators import (
    CaloriesCalculator,
    DistanceCalculator,
    ElevationGainCalculator,
    HeartRateCalculator,
    MovingTimeCalculator,
    PerceivedExertionCalculator,
)
from src.core.activities.summary.ports import (
    ActivityDataLoader,
    ActivitySummaryPresenter,
    MetricCalculator,
    SummaryBuilder,
    SummaryData,
)


class ActivitySummaryService:
    def __init__(
        self,
        data_loader: ActivityDataLoader,
        summary_builder: SummaryBuilder,
        presenter: ActivitySummaryPresenter,
    ) -> None:
        self.data_loader = data_loader
        self.summary_builder = summary_builder
        self.presenter = presenter
        self.calculators: list[MetricCalculator] = [
            DistanceCalculator(),
            MovingTimeCalculator(),
            ElevationGainCalculator(),
            HeartRateCalculator(),
            CaloriesCalculator(),
            PerceivedExertionCalculator(),
        ]

    def generate_summary(self) -> None:
        activities = self.data_loader.load_activities()
        self.summary_builder.reset()

        # Calculate each metric
        for calculator in self.calculators:
            result = calculator.calculate(activities)
            self._update_summary(result)

        self.presenter.present_weekly_report(self.summary_builder.get_summary())

    def _update_summary(self, result: SummaryData) -> None:
        if "total_distance" in result:
            self.summary_builder.add_distance(result["total_distance"])
        if "total_moving_time" in result:
            self.summary_builder.add_moving_time(result["total_moving_time"])
        if "total_elevation_gain" in result:
            self.summary_builder.add_elevation_gain(result["total_elevation_gain"])
        if "avg_heartrate" in result and "avg_max_heartrate" in result:
            self.summary_builder.add_heart_rate_metrics(
                result["avg_heartrate"], result["avg_max_heartrate"]
            )
        if "total_calories" in result:
            self.summary_builder.add_calories(result["total_calories"])
        if "avg_perceived_exertion" in result:
            self.summary_builder.add_perceived_exertion(
                result["avg_perceived_exertion"]
            )
