"""Advanced column operations for sophisticated data transformations."""

from typing import Any, Callable, Dict, List
import pandas as pd
import numpy as np
from functools import reduce
import re


class ColumnOperation:
    """Base class for column operations."""

    def apply(self, series: pd.Series, **kwargs) -> pd.Series:
        """Apply the operation to a pandas Series."""
        raise NotImplementedError


class MapOperation(ColumnOperation):
    """Apply a mapping function to each element in a column."""

    def __init__(self, func_str: str, safe_functions: Dict[str, Any]):
        """Initialize with a function string and safe functions."""
        self.func_str = func_str
        self.safe_functions = safe_functions
        self.compiled_func = self._compile_function()

    def _compile_function(self) -> Callable:
        """Compile the function string into a callable."""
        # Create a safe environment for the function
        safe_env = {
            **self.safe_functions,
            "str": str,
            "int": int,
            "float": float,
            "bool": bool,
            "len": len,
            "abs": abs,
            "round": round,
            "max": max,
            "min": min,
            "re": re,
            "pd": pd,
            "np": np,
        }

        try:
            # Support both lambda and regular function definitions
            if self.func_str.strip().startswith("lambda"):
                return eval(self.func_str, {"__builtins__": {}}, safe_env)
            else:
                # For more complex functions, wrap in a lambda
                return eval(
                    f"lambda x: {self.func_str}", {"__builtins__": {}}, safe_env
                )
        except Exception as e:
            raise ValueError(f"Invalid function: {self.func_str}. Error: {str(e)}")

    def apply(self, series: pd.Series, **kwargs) -> pd.Series:
        """Apply the mapping function to each element."""
        try:
            return series.map(self.compiled_func)
        except Exception as e:
            raise ValueError(f"Map operation failed: {str(e)}")


class FilterOperation(ColumnOperation):
    """Filter elements in a column based on a condition."""

    def __init__(
        self,
        condition_str: str,
        safe_functions: Dict[str, Any],
        fill_value: Any = np.nan,
    ):
        """Initialize with condition string and fill value for filtered elements."""
        self.condition_str = condition_str
        self.safe_functions = safe_functions
        self.fill_value = fill_value
        self.compiled_condition = self._compile_condition()

    def _compile_condition(self) -> Callable:
        """Compile the condition string into a callable."""
        safe_env = {
            **self.safe_functions,
            "str": str,
            "int": int,
            "float": float,
            "bool": bool,
            "len": len,
            "abs": abs,
            "round": round,
            "max": max,
            "min": min,
            "re": re,
            "pd": pd,
            "np": np,
        }

        try:
            if self.condition_str.strip().startswith("lambda"):
                return eval(self.condition_str, {"__builtins__": {}}, safe_env)
            else:
                return eval(
                    f"lambda x: {self.condition_str}", {"__builtins__": {}}, safe_env
                )
        except Exception as e:
            raise ValueError(
                f"Invalid condition: {self.condition_str}. Error: {str(e)}"
            )

    def apply(self, series: pd.Series, **kwargs) -> pd.Series:
        """Apply the filter condition."""
        try:
            mask = series.map(self.compiled_condition)
            return series.where(mask, self.fill_value)
        except Exception as e:
            raise ValueError(f"Filter operation failed: {str(e)}")


class ReduceOperation(ColumnOperation):
    """Apply a reduce function to aggregate column values."""

    def __init__(
        self, func_str: str, safe_functions: Dict[str, Any], initial_value: Any = None
    ):
        """Initialize with reduce function and optional initial value."""
        self.func_str = func_str
        self.safe_functions = safe_functions
        self.initial_value = initial_value
        self.compiled_func = self._compile_function()

    def _compile_function(self) -> Callable:
        """Compile the reduce function string."""
        safe_env = {
            **self.safe_functions,
            "str": str,
            "int": int,
            "float": float,
            "bool": bool,
            "len": len,
            "abs": abs,
            "round": round,
            "max": max,
            "min": min,
            "re": re,
            "pd": pd,
            "np": np,
        }

        try:
            if self.func_str.strip().startswith("lambda"):
                return eval(self.func_str, {"__builtins__": {}}, safe_env)
            else:
                return eval(
                    f"lambda acc, x: {self.func_str}", {"__builtins__": {}}, safe_env
                )
        except Exception as e:
            raise ValueError(
                f"Invalid reduce function: {self.func_str}. Error: {str(e)}"
            )

    def apply(self, series: pd.Series, **kwargs) -> pd.Series:
        """Apply the reduce operation and broadcast result."""
        try:
            # Apply reduce to get single value
            if self.initial_value is not None:
                result = reduce(self.compiled_func, series.dropna(), self.initial_value)
            else:
                result = reduce(self.compiled_func, series.dropna())

            # Broadcast result to all rows
            return pd.Series([result] * len(series), index=series.index)
        except Exception as e:
            raise ValueError(f"Reduce operation failed: {str(e)}")


class GroupOperation(ColumnOperation):
    """Group-based operations on columns."""

    def __init__(self, group_by: str, agg_func: str, safe_functions: Dict[str, Any]):
        """Initialize with grouping column and aggregation function."""
        self.group_by = group_by
        self.agg_func = agg_func
        self.safe_functions = safe_functions

    def apply(self, series: pd.Series, **kwargs) -> pd.Series:
        """Apply group-based operation."""
        df = kwargs.get("dataframe")
        if df is None:
            raise ValueError("GroupOperation requires the full DataFrame")

        if self.group_by not in df.columns:
            raise ValueError(f"Group by column '{self.group_by}' not found")

        try:
            # Group by the specified column and apply aggregation
            grouped = df.groupby(self.group_by)[series.name].agg(self.agg_func)
            # Map back to original series
            return df[self.group_by].map(grouped)
        except Exception as e:
            raise ValueError(f"Group operation failed: {str(e)}")


class WindowOperation(ColumnOperation):
    """Rolling window operations on columns."""

    def __init__(self, window_size: int, func_str: str, safe_functions: Dict[str, Any]):
        """Initialize with window size and function."""
        self.window_size = window_size
        self.func_str = func_str
        self.safe_functions = safe_functions

    def apply(self, series: pd.Series, **kwargs) -> pd.Series:
        """Apply rolling window operation."""
        try:
            rolling = series.rolling(window=self.window_size)

            # Apply standard aggregation functions
            if self.func_str == "mean":
                return rolling.mean()
            elif self.func_str == "sum":
                return rolling.sum()
            elif self.func_str == "max":
                return rolling.max()
            elif self.func_str == "min":
                return rolling.min()
            elif self.func_str == "std":
                return rolling.std()
            elif self.func_str == "count":
                return rolling.count()
            else:
                # Custom function
                safe_env = {**self.safe_functions, "np": np, "pd": pd}
                func = eval(
                    f"lambda x: {self.func_str}", {"__builtins__": {}}, safe_env
                )
                return rolling.apply(func)

        except Exception as e:
            raise ValueError(f"Window operation failed: {str(e)}")


class AdvancedColumnTransformer:
    """Handles advanced column transformations with map/reduce/filter operations."""

    def __init__(self, safe_functions: Dict[str, Any]):
        """Initialize with safe functions."""
        self.safe_functions = safe_functions

    def parse_operation(self, operation_config: Dict[str, Any]) -> ColumnOperation:
        """Parse operation configuration and return appropriate operation."""
        op_type = operation_config.get("type")

        if op_type == "map":
            return MapOperation(operation_config["function"], self.safe_functions)
        elif op_type == "filter":
            return FilterOperation(
                operation_config["condition"],
                self.safe_functions,
                operation_config.get("fill_value", np.nan),
            )
        elif op_type == "reduce":
            return ReduceOperation(
                operation_config["function"],
                self.safe_functions,
                operation_config.get("initial_value"),
            )
        elif op_type == "group":
            return GroupOperation(
                operation_config["group_by"],
                operation_config["function"],
                self.safe_functions,
            )
        elif op_type == "window":
            return WindowOperation(
                operation_config["window_size"],
                operation_config["function"],
                self.safe_functions,
            )
        else:
            raise ValueError(f"Unsupported operation type: {op_type}")

    def apply_operations(
        self, series: pd.Series, operations: List[Dict[str, Any]], **kwargs
    ) -> pd.Series:
        """Apply a sequence of operations to a series."""
        result = series.copy()

        for op_config in operations:
            operation = self.parse_operation(op_config)
            result = operation.apply(result, **kwargs)

        return result
