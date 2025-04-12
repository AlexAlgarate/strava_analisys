from typing import Any, Dict, List

import pandas as pd

from src.interfaces.console_printer import PrinterResultInterface


class ResultConsolePrinter(PrinterResultInterface):
    def print_result(self, option: str, result: Dict | List | pd.DataFrame) -> None:
        print(f"\n✅ Result for option {option}:\n")

        if isinstance(result, pd.DataFrame):
            self._print_dataframe(result)
        elif isinstance(result, list):
            self._print_list(result)
        elif isinstance(result, dict):
            self._print_dict(result)
        else:
            print("No data available")

    def _print_dict(self, data: Dict[str, Any], indent: int = 0) -> None:
        for key, value in data.items():
            prefix = "  " * indent
            if isinstance(value, dict):
                print(f"{prefix}📌 {key}:")
                self._print_dict(value, indent + 1)
            elif isinstance(value, list):
                print(f"{prefix}📌 {key}:")
                self._print_list(value, indent + 1)
            else:
                print(f"{prefix}• {key}: {value}")

    def _print_list(self, data: List[Any], indent: int = 0) -> None:
        for item in data:
            prefix = "  " * indent
            if isinstance(item, dict):
                print(f"\n{prefix}---\n")
                self._print_dict(item, indent)
            else:
                print(f"{prefix}• {item}")

    def _print_dataframe(self, df: pd.DataFrame) -> None:
        pd.set_option("display.max_columns", None)
        pd.set_option("display.expand_frame_repr", False)
        print(df)
