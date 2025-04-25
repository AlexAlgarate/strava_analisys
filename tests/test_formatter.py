import pytest

from src.menu.formatter import (
    ActivityCaloriesFormatter,
    ActivityDateFormatter,
    ActivityDistanceFormatter,
    ActivityDurationFormatter,
    ActivityExertionFormatter,
    ActivityHeartRateFormatter,
    ActivityPaceFormatter,
)


class TestValidFormatter:
    invalid_inputs: list = ["abc", None, {}, [], "", "  "]

    @pytest.mark.parametrize(
        "formatter_cls, input_value, expected_output",
        [
            (ActivityDateFormatter, "2025-04-16T10:30:00Z", "2025-04-16 10:30:00"),
            (ActivityDateFormatter, "1990-01-01T01:01:00Z", "1990-01-01 01:01:00"),
            (ActivityDistanceFormatter, 1000, "1.00 km"),
            (ActivityDistanceFormatter, 100, "0.10 km"),
            (ActivityPaceFormatter, 5, "18.00 km/h"),
            (ActivityPaceFormatter, 2.5, "9.00 km/h"),
            (ActivityDurationFormatter, 65, "1m 5s"),
            (ActivityDurationFormatter, 3600, "60m 0s"),
            (ActivityHeartRateFormatter, 65, "65 ppm"),
            (ActivityHeartRateFormatter, 180, "180 ppm"),
            (ActivityCaloriesFormatter, 12345, "12345 kcal"),
            (ActivityCaloriesFormatter, 0, "0 kcal"),
            (ActivityExertionFormatter, 5, "5 RPE"),
            (ActivityExertionFormatter, 10, "10 RPE"),
        ],
    )
    def test_valid_formatter(self, formatter_cls, input_value, expected_output):
        formatter = formatter_cls()
        assert formatter.format(input_value) == expected_output

    @pytest.mark.parametrize(
        "formatter_cls",
        [
            ActivityDateFormatter,
            ActivityDistanceFormatter,
            ActivityPaceFormatter,
            ActivityDurationFormatter,
            ActivityHeartRateFormatter,
            ActivityCaloriesFormatter,
            ActivityExertionFormatter,
        ],
    )
    @pytest.mark.parametrize("invalid_input", invalid_inputs)
    def test_invalid_inputs_return_str(self, formatter_cls, invalid_input):
        formatter = formatter_cls()
        assert formatter.format(invalid_input) == str(invalid_input)
