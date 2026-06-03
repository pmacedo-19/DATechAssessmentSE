import logging
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

logger = logging.getLogger(__name__)


class TransformError(Exception):
    """Custom exception for transformation errors."""

    pass


class DataTransformer:
    """Transform financial instrument data to CSV format.

    This class converts parsed XML data to CSV files
    and adds computed columns.
    """

    REQUIRED_COLUMNS = [
        "FinInstrmGnlAttrbts.Id",
        "FinInstrmGnlAttrbts.FullNm",
        "FinInstrmGnlAttrbts.ClssfctnTp",
        "FinInstrmGnlAttrbts.CmmdtyDerivInd",
        "FinInstrmGnlAttrbts.NtnlCcy",
        "Issr",
    ]

    def __init__(self) -> None:
        """Initialize data transformer."""
        self.logger = logging.getLogger(__name__)

    def to_csv(self, data: List[Dict[str, Any]], output_path: str) -> None:
        """Convert data to CSV file.

        Args:
            data: List of dictionaries with financial instrument data
            output_path: Path to output CSV file

        Raises:
            TransformError: If conversion fails
        """
        try:
            self.logger.info(f"Converting data to CSV: {output_path}")

            df = pd.DataFrame(data)

            # Verify required columns exist
            missing_cols = set(self.REQUIRED_COLUMNS) - set(df.columns)
            if missing_cols:
                raise TransformError(f"Missing columns: {missing_cols}")

            # Select required columns in order
            df = df[self.REQUIRED_COLUMNS]

            # Write to CSV
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(output_path, index=False)

            self.logger.info(f"Successfully wrote {len(df)} rows to {output_path}")

        except Exception as e:
            raise TransformError(f"Failed to convert to CSV: {e}")

    def add_a_count_column(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add column counting lowercase 'a' in FullNm field.

        Args:
            df: DataFrame with financial instrument data

        Returns:
            DataFrame with new 'a_count' column

        Raises:
            TransformError: If column missing
        """
        try:
            self.logger.info("Adding 'a_count' column")

            if "FinInstrmGnlAttrbts.FullNm" not in df.columns:
                raise TransformError("FinInstrmGnlAttrbts.FullNm column not found")

            df["a_count"] = (
                df["FinInstrmGnlAttrbts.FullNm"]
                .str.lower()
                .str.count("a")
                .fillna(0)
                .astype(int)
            )

            self.logger.info("Successfully added 'a_count' column")
            return df

        except Exception as e:
            raise TransformError(f"Failed to add a_count column: {e}")

    def add_contains_a_column(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add column indicating if 'a' is present in FullNm.

        Args:
            df: DataFrame with 'a_count' column

        Returns:
            DataFrame with new 'contains_a' column

        Raises:
            TransformError: If a_count column missing
        """
        try:
            self.logger.info("Adding 'contains_a' column")

            if "a_count" not in df.columns:
                raise TransformError("a_count column not found")

            df["contains_a"] = df["a_count"].apply(lambda x: "YES" if x > 0 else "NO")

            self.logger.info("Successfully added 'contains_a' column")
            return df

        except Exception as e:
            raise TransformError(f"Failed to add contains_a column: {e}")
