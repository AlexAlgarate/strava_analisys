from typing import Any, Dict, List

import pandas as pd

from src.interfaces.console_printer import IPrinterResult
from src.menu.formatter import ActivityFormatter


class ResultConsolePrinter(IPrinterResult):
    def __init__(self):
        self.formatter = ActivityFormatter()

    def print_result(self, option: str, result: Dict | List | pd.DataFrame) -> None:
        print(f"\n✅ Result for option {option}:\n")

        if isinstance(result, pd.DataFrame):
            self._print_dataframe(result)
        elif isinstance(result, list):
            self._print_activities_list(result)
        elif isinstance(result, dict):
            self._print_activity_dict(result)
        else:
            print("No data available")

    def _print_activity_dict(self, data: Dict[str, Any], indent: int = 0) -> None:
        for key, value in data.items():
            prefix = "  " * indent
            if isinstance(value, (dict, list)):
                print(f"{prefix}📌 {self.formatter.format_key(key)}:")
                self._print_activity_dict(value, indent + 1) if isinstance(
                    value, dict
                ) else self._print_activities_list(value, indent + 1)
            else:
                print(
                    f"{prefix}• {self.formatter.format_key(key)}: {self.formatter.format_value(key, value)}"
                )

    def _print_activities_list(self, data: List[Any], indent: int = 0) -> None:
        for item in data:
            if isinstance(item, dict):
                print(f"\n{'  ' * indent}━━━ Activity ━━━")
                self._print_activity_dict(item, indent)
                print(f"\n{'  ' * indent}━━━━━━━━━━━━━━\n")

    def _print_dataframe(self, df: pd.DataFrame) -> None:
        pd.set_option("display.max_columns", None)
        pd.set_option("display.expand_frame_repr", False)
        pd.set_option("display.float_format", lambda x: f"{x:.2f}")
        print(df)
