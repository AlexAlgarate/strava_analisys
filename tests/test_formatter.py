from typing import ClassVar

import pytest

from src.presentation.console_output.formatter import (
    ActivityCaloriesFormatter,
    ActivityDistanceFormatter,
    ActivityDurationFormatter,
    ActivityFormatter,
    ActivityHeartRateFormatter,
    ActivitySpeedFormatter,
    ValueFormatter,
)


class TestActivityFormatters:
    invalid_inputs: ClassVar[list[object]] = [
        "abc",
        None,
        {},
        [],
        "",
        "  ",
        True,
    ]

    @pytest.mark.parametrize(
        ("formatter_cls", "input_value", "expected_output"),
        [
            (ActivityDistanceFormatter, 1000, "1.00 km"),
            (ActivityDistanceFormatter, 100, "0.10 km"),
            (ActivitySpeedFormatter, 5, "18.00 km/h"),
            (ActivitySpeedFormatter, 2.5, "9.00 km/h"),
            (ActivityDurationFormatter, 65, "1m 5s"),
            (ActivityDurationFormatter, 3600, "60m 0s"),
            (ActivityHeartRateFormatter, 65, "65 bpm"),
            (ActivityHeartRateFormatter, 180, "180 bpm"),
            (ActivityCaloriesFormatter, 12345, "12345 kcal"),
            (ActivityCaloriesFormatter, 0, "0 kcal"),
        ],
    )
    def test_formats_supported_metric_values(
        self,
        formatter_cls: type[ValueFormatter],
        input_value: float | str,
        expected_output: str,
    ) -> None:
        formatter = formatter_cls()
        assert formatter.format(input_value) == expected_output

    @pytest.mark.parametrize(
        "formatter_cls",
        [
            ActivityDistanceFormatter,
            ActivitySpeedFormatter,
            ActivityDurationFormatter,
            ActivityHeartRateFormatter,
            ActivityCaloriesFormatter,
        ],
    )
    @pytest.mark.parametrize("invalid_input", invalid_inputs)
    def test_returns_original_text_for_invalid_metric_values(
        self, formatter_cls: type[ValueFormatter], invalid_input: object
    ) -> None:
        formatter = formatter_cls()
        assert formatter.format(invalid_input) == str(invalid_input)


def test_activity_formatter_exposes_explicit_metric_operations() -> None:
    formatter = ActivityFormatter()

    assert formatter.format_distance(1_000) == "1.00 km"
    assert formatter.format_speed(5) == "18.00 km/h"
    assert formatter.format_duration(65) == "1m 5s"
    assert formatter.format_heart_rate(145) == "145 bpm"
    assert formatter.format_calories(650) == "650 kcal"
