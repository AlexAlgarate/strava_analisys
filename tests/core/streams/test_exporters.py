import os
from tempfile import TemporaryDirectory

import pandas as pd
import pytest

from src.core.streams.exporter import DataExporter
from src.core.streams.exporters.csv_exporter import CsvExporter
from src.core.streams.exporters.exporter_interface import StreamExporter


class MockExporter(StreamExporter):
    def export(self, df: pd.DataFrame, path: str) -> None:
        pass


class TestStreamExporter:
    @pytest.fixture
    def sample_df(self):
        return pd.DataFrame(
            {
                "time": [0, 1, 2],
                "distance": [0, 100, 200],
                "heartrate": [60, 65, 70],
                "id": [1, 1, 1],
            }
        )

    def test_csv_exporter(self, sample_df):
        with TemporaryDirectory() as tmp_dir:
            path = f"{tmp_dir}/test.csv"
            exporter = CsvExporter()
            exporter.export(sample_df, path)

            assert os.path.exists(path)
            result_df = pd.read_csv(path)
            pd.testing.assert_frame_equal(result_df, sample_df)


class TestDataExporter:
    @pytest.fixture
    def sample_df(self):
        return pd.DataFrame({"time": [0, 1], "distance": [0, 100], "id": [1, 1]})

    def test_default_exporter_initialization(self):
        exporter = DataExporter()
        assert "csv" in exporter.exporter
        assert isinstance(exporter.exporter["csv"], CsvExporter)

    def test_custom_exporter_initialization(self):
        mock_exporter = MockExporter()
        exporter = DataExporter({"mock": mock_exporter})
        assert "mock" in exporter.exporter
        assert exporter.exporter["mock"] == mock_exporter

    def test_create_path(self):
        exporter = DataExporter()
        path = exporter._create_path("output", True, "csv")
        assert path == "output/streams_previous_week.csv"

        path = exporter._create_path("output", False, "csv")
        assert path == "output/streams_current_week.csv"

    def test_export_streams_invalid_format(self, sample_df):
        exporter = DataExporter()
        with pytest.raises(ValueError, match="Unsupported format: invalid"):
            exporter.export_streams(sample_df, selected_format="invalid")

    def test_export_streams_success(self, sample_df):
        with TemporaryDirectory() as tmp_dir:
            exporter = DataExporter()
            exporter.export_streams(
                sample_df, selected_format="csv", output_dir=tmp_dir, previous_week=True
            )

            expected_path = f"{tmp_dir}/streams_previous_week.csv"
            assert os.path.exists(expected_path)
            result_df = pd.read_csv(expected_path)
            pd.testing.assert_frame_equal(result_df, sample_df)
