from abc import ABC, abstractmethod

import pandas as pd


class IPrinterResult(ABC):
    @abstractmethod
    def print_result(self, option: str, result: dict | list | pd.DataFrame) -> None:
        pass


class IPrinterError(ABC):
    @abstractmethod
    def print_error(self, option: str) -> None:
        pass
