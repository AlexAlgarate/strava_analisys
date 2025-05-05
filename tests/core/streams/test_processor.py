import pandas as pd

from src.core.streams.processor import process_streams


class TestStreamProcessor:
    def test_process_streams_basic(self):
        test_data = {
            "time": {"data": [0, 1, 2]},
            "distance": {"data": [0, 100, 200]},
            "heartrate": {"data": [60, 65, 70]},
        }

        result = process_streams(test_data, id_activity=123)

        assert isinstance(result, pd.DataFrame)
        assert list(result.columns) == ["time", "distance", "heartrate", "id"]
        assert len(result) == 3
        assert all(result["id"] == 123)

    def test_process_streams_empty_data(self):
        test_data = {
            "time": {"data": []},
            "distance": {"data": []},
            "heartrate": {"data": []},
        }

        result = process_streams(test_data, id_activity=123)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
        assert "id" in result.columns

    def test_process_streams_missing_data(self):
        test_data = {
            "time": {"data": [0, 1]},
            "distance": {},  # Missing data
            "heartrate": {"data": [60, 65]},
        }

        result = process_streams(test_data, id_activity=123)

        assert isinstance(result, pd.DataFrame)
        assert list(result.columns) == ["time", "distance", "heartrate", "id"]
        assert len(result) == 2
        assert all(result["distance"].isna())  # Distance column should be NaN

    def test_process_streams_uneven_data(self):
        test_data = {
            "time": {"data": [0, 1, 2]},
            "distance": {"data": [0, 100]},  # One less data point
            "heartrate": {"data": [60, 65, 70, 75]},  # One more data point
        }

        result = process_streams(test_data, id_activity=123)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3  # Should use max length
        assert result["distance"].isna().sum() == 1  # Last value should be NaN
        assert all(~result["time"].isna())  # Time should have no NaN values
