"""Main transformation engine for data processing."""

from typing import Any, Dict, List, Optional, Union
import pandas as pd
import numpy as np
import re
from .expressions import ExpressionParser
from .column_operations import AdvancedColumnTransformer
from .dependency_resolver import ColumnExecutionEngine


class ValidationError(Exception):
    """Exception raised when data validation fails."""

    pass


class TransformationEngine:
    """Engine for applying transformations and validations to data."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize transformation engine with configuration."""
        self.config = config
        self.expression_parser = ExpressionParser()
        self.column_transformer = AdvancedColumnTransformer(
            self.expression_parser.safe_parser.SAFE_FUNCTIONS
        )
        self.execution_engine = ColumnExecutionEngine()
        self.errors: List[Dict[str, Any]] = []
        self.max_errors = config.get("global_settings", {}).get("max_errors", 100)
        self.ignore_errors = config.get("global_settings", {}).get(
            "ignore_errors", False
        )
        self.execution_plan: Optional[Dict[str, Any]] = None

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply all transformations to the DataFrame with dependency resolution."""
        self.errors.clear()

        output_columns = self.config["output"]["columns"]
        input_columns = set(df.columns)

        # Plan execution with dependency resolution
        try:
            self.execution_plan = self.execution_engine.plan_execution(
                output_columns, input_columns
            )

            if self.config.get("global_settings", {}).get("show_execution_plan", False):
                self._log_execution_plan()

        except Exception as e:
            self._handle_error(f"Execution planning failed: {str(e)}")
            # Fall back to original order if planning fails
            execution_order = list(output_columns.keys())
            self.execution_plan = {
                "execution_order": execution_order,
                "final_columns": execution_order,
                "interim_columns": [],
            }

        # Start with input DataFrame
        result_df = df.copy()

        # Process columns in dependency order
        execution_order = self.execution_plan["execution_order"]

        for column_name in execution_order:
            column_config = output_columns[column_name]
            try:
                # Process the column and add to result
                result_df[column_name] = self._process_column(
                    result_df, column_name, column_config
                )

                # Log progress for debugging
                if self.config.get("global_settings", {}).get("verbose", False):
                    print(f"✓ Processed column: {column_name}")

            except Exception as e:
                self._handle_error(f"Error processing column '{column_name}': {str(e)}")
                if not self.ignore_errors:
                    continue

        # Filter out interim columns from final result
        final_columns = self.execution_plan.get(
            "final_columns", list(output_columns.keys())
        )

        # Keep input columns and final output columns
        columns_to_keep = list(input_columns) + [
            col for col in final_columns if col in result_df.columns
        ]

        # Remove duplicates while preserving order
        seen = set()
        columns_to_keep = [
            col for col in columns_to_keep if not (col in seen or seen.add(col))
        ]

        # If user specified to only keep output columns, filter input columns too
        if self.config["output"].get("only_output_columns", False):
            columns_to_keep = [col for col in final_columns if col in result_df.columns]

        result_df = result_df[columns_to_keep]

        # Apply filters
        if "filters" in self.config["output"]:
            result_df = self._apply_filters(result_df)

        # Apply sorting
        if "sort" in self.config["output"]:
            result_df = self._apply_sorting(result_df)

        return result_df

    def _log_execution_plan(self) -> None:
        """Log the execution plan for debugging."""
        if not self.execution_plan:
            return

        print("=== EXECUTION PLAN ===")
        print(f"Total columns to process: {self.execution_plan['total_steps']}")
        print(f"Execution order: {' -> '.join(self.execution_plan['execution_order'])}")
        print(f"Interim columns: {self.execution_plan['interim_columns']}")
        print(f"Final columns: {self.execution_plan['final_columns']}")

        # Show dependency information
        dep_info = self.execution_plan.get("dependency_info", {})
        if dep_info.get("dependency_graph"):
            print("\nDependencies:")
            for col, deps in dep_info["dependency_graph"].items():
                if deps:
                    print(f"  {col} depends on: {', '.join(sorted(deps))}")
        print("======================")

    def _process_column(
        self, df: pd.DataFrame, column_name: str, column_config: Dict[str, Any]
    ) -> pd.Series:
        """Process a single column according to its configuration."""
        # Get source data
        if "operations" in column_config:
            # Advanced column operations (map/reduce/filter)
            source = column_config.get("source", column_name)
            if source in df.columns:
                series = df[source].copy()
            else:
                # Try to evaluate as expression first
                try:
                    series = self.expression_parser.evaluate_vectorized(source, df)
                except Exception:
                    raise ValueError(f"Source column '{source}' not found")

            # Apply advanced operations
            operations = column_config["operations"]
            series = self.column_transformer.apply_operations(
                series, operations, dataframe=df
            )

        elif "transformation" in column_config:
            # Apply transformation expression
            transformation = column_config["transformation"]
            series = self.expression_parser.evaluate_vectorized(transformation, df)
        else:
            # Simple column mapping
            source = column_config.get("source", column_name)
            if source in df.columns:
                series = df[source].copy()
            else:
                # Try to evaluate as expression
                try:
                    series = self.expression_parser.evaluate_vectorized(source, df)
                except Exception:
                    raise ValueError(f"Source column '{source}' not found")

        # Apply data type conversion
        target_type = column_config.get("type", "string")
        series = self._convert_type(series, target_type, column_config.get("format"))

        # Apply default values
        if "default" in column_config:
            default_value = column_config["default"]
            series = series.fillna(default_value)

        # Validate data
        if "validation" in column_config:
            series = self._validate_column(
                series, column_name, column_config["validation"]
            )

        return series

    def _convert_type(
        self, series: pd.Series, target_type: str, format_str: Optional[str] = None
    ) -> pd.Series:
        """Convert series to target data type."""
        try:
            if target_type == "string":
                return series.astype(str)
            elif target_type == "int":
                return pd.to_numeric(series, errors="coerce").astype("Int64")
            elif target_type == "float":
                return pd.to_numeric(series, errors="coerce")
            elif target_type == "bool":
                return series.astype(bool)
            elif target_type == "datetime":
                if format_str:
                    return pd.to_datetime(series, format=format_str, errors="coerce")
                else:
                    return pd.to_datetime(series, errors="coerce")
            else:
                raise ValueError(f"Unsupported data type: {target_type}")
        except Exception as e:
            raise ValueError(f"Type conversion failed: {str(e)}")

    def _validate_column(
        self, series: pd.Series, column_name: str, validation_rules: Dict[str, Any]
    ) -> pd.Series:
        """Validate column data according to validation rules."""
        errors = []

        # Required validation
        if validation_rules.get("required", True):
            null_mask = series.isna()
            if null_mask.any():
                null_indices = series[null_mask].index.tolist()
                errors.append(
                    f"Required field '{column_name}' has null values at indices: {null_indices}"
                )

        # Nullable validation
        if not validation_rules.get("nullable", False):
            null_mask = series.isna()
            if null_mask.any():
                null_indices = series[null_mask].index.tolist()
                errors.append(
                    f"Non-nullable field '{column_name}' has null values at indices: {null_indices}"
                )

        # Numeric validations
        if "min_value" in validation_rules:
            min_val = validation_rules["min_value"]
            invalid_mask = series < min_val
            if invalid_mask.any():
                invalid_indices = series[invalid_mask].index.tolist()
                errors.append(
                    f"Field '{column_name}' has values below minimum ({min_val}) at indices: {invalid_indices}"
                )

        if "max_value" in validation_rules:
            max_val = validation_rules["max_value"]
            invalid_mask = series > max_val
            if invalid_mask.any():
                invalid_indices = series[invalid_mask].index.tolist()
                errors.append(
                    f"Field '{column_name}' has values above maximum ({max_val}) at indices: {invalid_indices}"
                )

        # String length validations
        if "min_length" in validation_rules:
            min_len = validation_rules["min_length"]
            string_series = series.astype(str)
            invalid_mask = string_series.str.len() < min_len
            if invalid_mask.any():
                invalid_indices = series[invalid_mask].index.tolist()
                errors.append(
                    f"Field '{column_name}' has values shorter than minimum length ({min_len}) at indices: {invalid_indices}"
                )

        if "max_length" in validation_rules:
            max_len = validation_rules["max_length"]
            string_series = series.astype(str)
            invalid_mask = string_series.str.len() > max_len
            if invalid_mask.any():
                invalid_indices = series[invalid_mask].index.tolist()
                errors.append(
                    f"Field '{column_name}' has values longer than maximum length ({max_len}) at indices: {invalid_indices}"
                )

        # Pattern validation
        if "pattern" in validation_rules:
            pattern = validation_rules["pattern"]
            string_series = series.astype(str)
            try:
                invalid_mask = ~string_series.str.match(pattern, na=False)
                if invalid_mask.any():
                    invalid_indices = series[invalid_mask].index.tolist()
                    errors.append(
                        f"Field '{column_name}' has values not matching pattern '{pattern}' at indices: {invalid_indices}"
                    )
            except re.error as e:
                errors.append(
                    f"Invalid regex pattern for field '{column_name}': {str(e)}"
                )

        # Allowed values validation
        if "allowed_values" in validation_rules:
            allowed_values = validation_rules["allowed_values"]
            invalid_mask = ~series.isin(allowed_values)
            if invalid_mask.any():
                invalid_indices = series[invalid_mask].index.tolist()
                errors.append(
                    f"Field '{column_name}' has values not in allowed list {allowed_values} at indices: {invalid_indices}"
                )

        # Handle validation errors
        for error in errors:
            self._handle_error(error)

        return series

    def _apply_filters(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply filters to the DataFrame."""
        filters = self.config["output"]["filters"]

        for filter_config in filters:
            condition = filter_config["condition"]
            action = filter_config.get("action", "keep")

            try:
                # Evaluate condition
                mask = self.expression_parser.evaluate_vectorized(condition, df)

                if action == "keep":
                    df = df[mask]
                elif action == "remove":
                    df = df[~mask]

            except Exception as e:
                self._handle_error(f"Error applying filter '{condition}': {str(e)}")

        return df

    def _apply_sorting(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply sorting to the DataFrame."""
        sort_configs = self.config["output"]["sort"]

        sort_columns = []
        sort_ascending = []

        for sort_config in sort_configs:
            column = sort_config["column"]
            ascending = sort_config.get("ascending", True)

            if column in df.columns:
                sort_columns.append(column)
                sort_ascending.append(ascending)
            else:
                self._handle_error(f"Sort column '{column}' not found in DataFrame")

        if sort_columns:
            try:
                df = df.sort_values(sort_columns, ascending=sort_ascending)
            except Exception as e:
                self._handle_error(f"Error sorting DataFrame: {str(e)}")

        return df

    def _handle_error(self, error_message: str) -> None:
        """Handle validation and processing errors."""
        self.errors.append({"message": error_message, "timestamp": pd.Timestamp.now()})

        if len(self.errors) >= self.max_errors:
            raise ValidationError(
                f"Maximum number of errors ({self.max_errors}) exceeded"
            )

        if not self.ignore_errors:
            raise ValidationError(error_message)

    def get_errors(self) -> List[Dict[str, Any]]:
        """Get list of validation errors."""
        return self.errors.copy()

    def has_errors(self) -> bool:
        """Check if there are any validation errors."""
        return len(self.errors) > 0
