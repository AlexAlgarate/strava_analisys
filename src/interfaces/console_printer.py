from abc import ABC, abstractmethod
from typing import Dict


class PrinterResultInterface(ABC):
    @abstractmethod
    def print_result(self, option: str, result: Dict) -> None:
        pass


class PrinterErrorInterface(ABC):
    @abstractmethod
    def print_error(self, option: str) -> None:
        pass


# class PrinterResultInterface(ABC):
# @abstractmethod
# def print_warning(self, warning: str) -> None:
#     pass
