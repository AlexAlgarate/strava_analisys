import os
from tempfile import TemporaryDirectory

import pandas as pd
import pytest

from src.core.streams.exporter import DataExporter
from src.core.streams.exporters.csv_exporter import CsvExporter
from src.core.streams.exporters.exporter_interface import StreamExporter


class MockExporter(StreamExporter):
    """Mock exporter for testing custom export formats."""

    def export(self, df: pd.DataFrame, path: str) -> None:
        pass


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        {
            "time": [0, 1, 2],
            "distance": [0, 100, 200],
            "heartrate": [60, 65, 70],
            "id": [1] * 3,
        }
    )


class TestStreamExporters:
    def test_csv_exporter(self, sample_df):
        with TemporaryDirectory() as tmp_dir:
            path = f"{tmp_dir}/test.csv"
            exporter = CsvExporter()
            exporter.export(sample_df, path)

            assert os.path.exists(path)
            result_df = pd.read_csv(path)
            pd.testing.assert_frame_equal(result_df, sample_df)


class TestDataExporter:
    def test_default_initialization(self):
        exporter = DataExporter()
        assert "csv" in exporter.exporter
        assert isinstance(exporter.exporter["csv"], CsvExporter)

    def test_custom_exporter_map(self):
        mock_exporter = MockExporter()
        exporter = DataExporter({"mock": mock_exporter})
        assert "mock" in exporter.exporter
        assert exporter.exporter["mock"] == mock_exporter

    def test_create_path(self):
        exporter = DataExporter()

        path = exporter._create_path("test_dir", True, "csv")
        assert path == "test_dir/streams_previous_week.csv"

        path = exporter._create_path("test_dir", False, "csv")
        assert path == "test_dir/streams_current_week.csv"

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

    def test_export_streams_custom_exporter(self, sample_df):
        class CountingExporter(StreamExporter):
            def __init__(self):
                self.export_count = 0

            def export(self, df: pd.DataFrame, path: str) -> None:
                self.export_count += 1

        counting_exporter = CountingExporter()
        exporter = DataExporter({"counter": counting_exporter})

        exporter.export_streams(sample_df, selected_format="counter")
        assert counting_exporter.export_count == 1
