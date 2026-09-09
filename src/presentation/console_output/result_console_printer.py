from collections.abc import Mapping, Sequence
from typing import cast

import pandas as pd

from src.domain.detailed_activity import DetailedActivity

from .formatter import ActivityFormatter


class ResultConsolePrinter:
    def __init__(self) -> None:
        self.formatter = ActivityFormatter()

    def print_result(self, option: str, result: object) -> None:
        print(f"\n✅ Result for option {option}:\n")

        if isinstance(result, pd.DataFrame):
            self._print_dataframe(result)
        elif isinstance(result, Sequence) and not isinstance(result, (str, bytes)):
            self._print_activities_list(result)
        elif isinstance(result, Mapping):
            self._print_activity_dict(result)
        else:
            print("No data available")

    def _print_activity_dict(
        self, data: Mapping[object, object], indent: int = 0
    ) -> None:
        for raw_key, value in data.items():
            key = str(raw_key)
            prefix = "  " * indent
            if isinstance(value, Mapping):
                print(f"{prefix}📌 {self.formatter.format_key(key)}:")
                self._print_activity_dict(value, indent + 1)
            elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
                print(f"{prefix}📌 {self.formatter.format_key(key)}:")
                self._print_activities_list(value, indent + 1)
            else:
                print(
                    f"{prefix}• {self.formatter.format_key(key)}: {self.formatter.format_value(key, value)}"
                )

    def _print_activities_list(self, data: Sequence[object], indent: int = 0) -> None:
        for item in data:
            if isinstance(item, DetailedActivity):
                item = item.as_dict()
            if isinstance(item, Mapping):
                print(f"\n{'  ' * indent}━━━ Activity ━━━")
                self._print_activity_dict(cast(Mapping[object, object], item), indent)
                print(f"\n{'  ' * indent}━━━━━━━━━━━━━━\n")

    def _print_dataframe(self, df: pd.DataFrame) -> None:
        pd.set_option("display.max_columns", None)
        pd.set_option("display.expand_frame_repr", False)
        pd.set_option("display.float_format", lambda x: f"{x:.2f}")
        print(df)
