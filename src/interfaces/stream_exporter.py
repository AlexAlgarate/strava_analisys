from abc import ABC, abstractmethod

import pandas as pd


class StreamExporter(ABC):
    @abstractmethod
    def export(self, df: pd.DataFrame, path: str) -> None:
        pass
