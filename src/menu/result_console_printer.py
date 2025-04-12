from typing import Dict

from src.interfaces.console_printer import PrinterResultInterface


class ResultConsolePrinter(PrinterResultInterface):
    def print_result(self, option: str, result: Dict) -> None:
        print(f"\n✅ Result for option {option}:\n")
        print(result)
