"""Join engine for handling multi-input data operations."""

from typing import Any, Dict, List, Union, Optional
import pandas as pd
from dataclasses import dataclass


@dataclass
class JoinConfig:
    """Configuration for a single join operation."""

    left: str
    right: str
    on: Union[str, List[str], Dict[str, str]]
    how: str = "inner"
    suffix: Optional[List[str]] = None

    def __post_init__(self):
        if self.how not in ["inner", "left", "right", "outer", "cross"]:
            raise ValueError(f"Invalid join type: {self.how}")


class JoinEngine:
    """Engine for performing data joins between multiple DataFrames."""

    def __init__(self):
        """Initialize the join engine."""
        self.datasets: Dict[str, pd.DataFrame] = {}
        self.join_history: List[Dict[str, Any]] = []

    def add_dataset(self, name: str, df: pd.DataFrame) -> None:
        """Add a named dataset to the engine."""
        if not isinstance(df, pd.DataFrame):
            raise TypeError("Dataset must be a pandas DataFrame")
        self.datasets[name] = df.copy()

    def perform_joins(self, join_configs: List[Dict[str, Any]]) -> pd.DataFrame:
        """Perform a series of joins according to configuration."""
        if not join_configs:
            # No joins specified - return first dataset or raise error
            if len(self.datasets) == 1:
                return list(self.datasets.values())[0]
            elif len(self.datasets) > 1:
                raise ValueError("Multiple inputs provided but no joins specified")
            else:
                raise ValueError("No datasets available")

        result_df = None

        for join_config_dict in join_configs:
            join_config = JoinConfig(**join_config_dict)

            # Get left dataset
            if join_config.left == "result" and result_df is not None:
                left_df = result_df
            elif join_config.left in self.datasets:
                left_df = self.datasets[join_config.left]
            else:
                raise ValueError(f"Left dataset '{join_config.left}' not found")

            # Get right dataset
            if join_config.right in self.datasets:
                right_df = self.datasets[join_config.right]
            else:
                raise ValueError(f"Right dataset '{join_config.right}' not found")

            # Perform the join
            result_df = self._perform_single_join(left_df, right_df, join_config)

            # Store join history for debugging
            self.join_history.append(
                {
                    "left": join_config.left,
                    "right": join_config.right,
                    "on": join_config.on,
                    "how": join_config.how,
                    "result_shape": result_df.shape,
                }
            )

        return result_df

    def _perform_single_join(
        self, left_df: pd.DataFrame, right_df: pd.DataFrame, config: JoinConfig
    ) -> pd.DataFrame:
        """Perform a single join operation."""
        # Handle different join key formats
        left_on: Union[str, List[str]]
        right_on: Union[str, List[str]]

        if isinstance(config.on, str):
            # Simple case: same column name in both datasets
            left_on = right_on = config.on
        elif isinstance(config.on, list):
            # List of column names (same in both datasets)
            left_on = right_on = config.on
        elif isinstance(config.on, dict):
            # Different column names: {"left": "col1", "right": "col2"}
            if "left" in config.on and "right" in config.on:
                left_on = config.on["left"]
                right_on = config.on["right"]
            else:
                # Dict mapping left columns to right columns
                left_on = list(config.on.keys())
                right_on = list(config.on.values())
        else:
            raise ValueError(f"Invalid join key format: {config.on}")

        # Validate join columns exist
        self._validate_join_columns(left_df, right_df, left_on, right_on)

        # Handle suffixes for overlapping columns
        suffixes = config.suffix or ["_left", "_right"]
        if len(suffixes) != 2:
            raise ValueError("Suffix must be a list of exactly 2 strings")

        try:
            # Perform the join
            if config.how == "cross":
                # Cross join doesn't use 'on' parameter
                result_df = left_df.merge(right_df, how="cross", suffixes=suffixes)
            else:
                result_df = left_df.merge(
                    right_df,
                    left_on=left_on,
                    right_on=right_on,
                    how=config.how,
                    suffixes=suffixes,
                )

            return result_df

        except Exception as e:
            raise ValueError(f"Join operation failed: {str(e)}")

    def _validate_join_columns(
        self,
        left_df: pd.DataFrame,
        right_df: pd.DataFrame,
        left_on: Union[str, List[str]],
        right_on: Union[str, List[str]],
    ) -> None:
        """Validate that join columns exist in their respective DataFrames."""
        # Ensure both are lists for consistent handling
        left_cols = [left_on] if isinstance(left_on, str) else left_on
        right_cols = [right_on] if isinstance(right_on, str) else right_on

        # Check left columns
        missing_left = [col for col in left_cols if col not in left_df.columns]
        if missing_left:
            raise ValueError(f"Left join columns not found: {missing_left}")

        # Check right columns
        missing_right = [col for col in right_cols if col not in right_df.columns]
        if missing_right:
            raise ValueError(f"Right join columns not found: {missing_right}")

        # Ensure same number of columns
        if len(left_cols) != len(right_cols):
            raise ValueError("Number of left and right join columns must match")

    def get_available_datasets(self) -> List[str]:
        """Get list of available dataset names."""
        return list(self.datasets.keys())

    def get_join_history(self) -> List[Dict[str, Any]]:
        """Get history of performed joins."""
        return self.join_history.copy()

    def get_dataset_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all loaded datasets."""
        info = {}
        for name, df in self.datasets.items():
            info[name] = {
                "shape": df.shape,
                "columns": list(df.columns),
                "dtypes": dict(df.dtypes.astype(str)),
                "memory_usage": df.memory_usage(deep=True).sum(),
            }
        return info
