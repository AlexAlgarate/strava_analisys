from abc import ABC, abstractmethod
from typing import Dict, List

import pandas as pd


class IPrinterResult(ABC):
    @abstractmethod
    def print_result(
        self, option: str, result: Dict | List | pd.DataFrame
    ) -> None:
        pass


class IPrinterError(ABC):
    @abstractmethod
    def print_error(self, option: str) -> None:
        pass
