import os
import tempfile

import pandas as pd
import pytest

from src.core.streams.exporter import CsvExporter, DataExporter
from src.interfaces.stream_exporter import IStreamExporter


class MockExporter(IStreamExporter):
    def export(self, df: pd.DataFrame, path: str) -> None:
        pass


@pytest.fixture
def sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "time": [0, 1, 2],
            "distance": [0, 100, 200],
            "heartrate": [60, 65, 70],
            "id": [1] * 3,
        }
    )


@pytest.fixture
def csv_exporter() -> CsvExporter:
    return CsvExporter()


@pytest.fixture
def data_exporter() -> DataExporter:
    return DataExporter()


class TestStreamExporters:
    def test_csv_exporter(
        self, sample_df: pd.DataFrame, csv_exporter: CsvExporter
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = f"{tmp_dir}/test.csv"

            csv_exporter.export(sample_df, path)

            assert os.path.exists(path)
            result_df = pd.read_csv(path)
            pd.testing.assert_frame_equal(result_df, sample_df)


class TestDataExporter:
    def test_default_initialization(self, data_exporter: DataExporter) -> None:
        assert "csv" in data_exporter.exporter
        assert isinstance(data_exporter.exporter["csv"], CsvExporter)

    def test_custom_exporter_initialization(self) -> None:
        mock_exporter = MockExporter()
        exporter = DataExporter({"mock": mock_exporter})
        assert "mock" in exporter.exporter
        assert exporter.exporter["mock"] == mock_exporter

    def test_create_path(self, data_exporter: DataExporter) -> None:
        path = data_exporter._create_path("test_dir", True, "csv")
        assert path == "test_dir/streams_previous_week.csv"

        path = data_exporter._create_path("test_dir", False, "csv")
        assert path == "test_dir/streams_current_week.csv"

    def test_export_streams_invalid_format(
        self, data_exporter: DataExporter, sample_df: pd.DataFrame
    ) -> None:
        with pytest.raises(ValueError, match="Unsupported format: invalid"):
            data_exporter.export_streams(sample_df, selected_format="invalid")

    def test_export_streams_success(
        self, data_exporter: DataExporter, sample_df: pd.DataFrame
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            data_exporter.export_streams(
                sample_df,
                selected_format="csv",
                output_dir=tmp_dir,
                previous_week=True,
            )

            expected_path = f"{tmp_dir}/streams_previous_week.csv"
            assert os.path.exists(expected_path)
            result_df = pd.read_csv(expected_path)
            pd.testing.assert_frame_equal(result_df, sample_df)

    def test_export_streams_custom_exporter(self, sample_df: pd.DataFrame) -> None:
        class CountingExporter(IStreamExporter):
            def __init__(self) -> None:
                self.export_count = 0

            def export(self, df: pd.DataFrame, path: str) -> None:
                self.export_count += 1

        counting_exporter = CountingExporter()
        exporter = DataExporter({"counter": counting_exporter})

        exporter.export_streams(sample_df, selected_format="counter")
        assert counting_exporter.export_count == 1
