import pandas as pd
import pytest

from esma_data_processor.transformer import (
    DataTransformer,
    TransformError,
)


class TestDataTransformer:
    """Test suite for DataTransformer class."""

    def test_to_csv_success(self, temp_dir, sample_data):
        """Test successful CSV creation."""
        transformer = DataTransformer()
        output_file = temp_dir / "output.csv"

        transformer.to_csv(sample_data, str(output_file))

        assert output_file.exists()

        # Verify CSV content
        df = pd.read_csv(output_file)
        assert len(df) == 2
        assert list(df.columns) == [
            "FinInstrmGnlAttrbts.Id",
            "FinInstrmGnlAttrbts.FullNm",
            "FinInstrmGnlAttrbts.ClssfctnTp",
            "FinInstrmGnlAttrbts.CmmdtyDerivInd",
            "FinInstrmGnlAttrbts.NtnlCcy",
            "Issr",
        ]

    def test_to_csv_missing_columns(self, temp_dir):
        """Test to_csv with missing required columns."""
        transformer = DataTransformer()
        output_file = temp_dir / "output.csv"

        incomplete_data = [{"Id": "TEST001"}]

        with pytest.raises(TransformError):
            transformer.to_csv(incomplete_data, str(output_file))

    def test_add_a_count_column(self, temp_dir, sample_data):
        """Test adding a_count column."""
        transformer = DataTransformer()
        df = pd.DataFrame(sample_data)

        result = transformer.add_a_count_column(df)

        assert "a_count" in result.columns
        assert result.loc[0, "a_count"] == 3  # "Test Financial Instrument A" has 3 a's
        assert result.loc[1, "a_count"] == 2  # "Another Test Value" has 2 a's

    def test_add_a_count_column_missing_fullname(self, temp_dir):
        """Test add_a_count with missing FullNm column."""
        transformer = DataTransformer()
        df = pd.DataFrame({"Id": ["TEST001"]})

        with pytest.raises(TransformError):
            transformer.add_a_count_column(df)

    def test_add_contains_a_column(self, temp_dir):
        """Test adding contains_a column."""
        transformer = DataTransformer()
        df = pd.DataFrame(
            {
                "a_count": [0, 1, 5],
            }
        )

        result = transformer.add_contains_a_column(df)

        assert "contains_a" in result.columns
        assert result.loc[0, "contains_a"] == "NO"
        assert result.loc[1, "contains_a"] == "YES"
        assert result.loc[2, "contains_a"] == "YES"

    def test_add_contains_a_column_missing_acount(self, temp_dir):
        """Test add_contains_a with missing a_count column."""
        transformer = DataTransformer()
        df = pd.DataFrame({"Id": ["TEST001"]})

        with pytest.raises(TransformError):
            transformer.add_contains_a_column(df)
