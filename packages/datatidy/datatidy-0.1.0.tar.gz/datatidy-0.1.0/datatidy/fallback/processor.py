"""Fallback processor for robust data processing with partial processing capabilities."""

from typing import Any, Dict, List, Optional, Callable
import pandas as pd
from dataclasses import dataclass
import time
from .logger import EnhancedLogger, ErrorCategory, ProcessingMode


@dataclass
class ProcessingResult:
    """Result of data processing with detailed information."""

    success: bool
    data: pd.DataFrame
    processing_mode: ProcessingMode
    successful_columns: List[str]
    failed_columns: List[str]
    skipped_columns: List[str]
    error_log: List[Dict[str, Any]]
    processing_time: float
    fallback_used: bool


class FallbackProcessor:
    """Enhanced processor with fallback capabilities and partial processing."""

    def __init__(self, config: Dict[str, Any], logger: Optional[EnhancedLogger] = None):
        """Initialize fallback processor."""
        self.config = config
        self.logger = logger or EnhancedLogger()

        # Processing settings
        global_settings = config.get("global_settings", {})
        self.processing_mode = ProcessingMode(
            global_settings.get("processing_mode", "strict")
        )
        self.max_column_failures = global_settings.get("max_column_failures", 10)
        self.failure_threshold = global_settings.get(
            "failure_threshold", 0.5
        )  # 50% failure rate
        self.enable_partial_processing = global_settings.get(
            "enable_partial_processing", True
        )
        self.enable_fallback = global_settings.get("enable_fallback", True)
        self.fallback_transformations = global_settings.get(
            "fallback_transformations", {}
        )

        # Initialize processing statistics
        self.reset_stats()

    def reset_stats(self):
        """Reset processing statistics."""
        self.successful_columns = []
        self.failed_columns = []
        self.skipped_columns = []
        self.column_processing_times = {}

    def process_with_fallback(
        self,
        df: pd.DataFrame,
        transformation_engine: Any,
        fallback_query_func: Optional[Callable] = None,
    ) -> ProcessingResult:
        """
        Process data with fallback capabilities.

        Args:
            df: Input DataFrame
            transformation_engine: Primary transformation engine
            fallback_query_func: Function to call for fallback data loading

        Returns:
            ProcessingResult with detailed processing information
        """
        start_time = time.time()
        self.reset_stats()

        output_columns = self.config["output"]["columns"]
        self.logger.start_processing(self.processing_mode, len(output_columns))

        try:
            if self.processing_mode == ProcessingMode.STRICT:
                result = self._process_strict_mode(df, transformation_engine)
            elif self.processing_mode == ProcessingMode.PARTIAL:
                result = self._process_partial_mode(df, transformation_engine)
            else:  # FALLBACK mode
                result = self._process_fallback_mode(
                    df, transformation_engine, fallback_query_func
                )

            processing_time = time.time() - start_time
            self.logger.end_processing(success=result.success)

            return ProcessingResult(
                success=result.success,
                data=result.data,
                processing_mode=self.processing_mode,
                successful_columns=self.successful_columns,
                failed_columns=self.failed_columns,
                skipped_columns=self.skipped_columns,
                error_log=self.logger.error_log,
                processing_time=processing_time,
                fallback_used=getattr(result, "fallback_used", False),
            )

        except Exception as e:
            processing_time = time.time() - start_time
            self.logger.log_column_error("SYSTEM", e, ErrorCategory.SYSTEM_ERROR)
            self.logger.end_processing(success=False)

            return ProcessingResult(
                success=False,
                data=df,
                processing_mode=self.processing_mode,
                successful_columns=self.successful_columns,
                failed_columns=self.failed_columns,
                skipped_columns=self.skipped_columns,
                error_log=self.logger.error_log,
                processing_time=processing_time,
                fallback_used=False,
            )

    def _process_strict_mode(
        self, df: pd.DataFrame, transformation_engine: Any
    ) -> ProcessingResult:
        """Process in strict mode - fail on any error."""
        try:
            result_df = transformation_engine.transform(df)
            self.successful_columns = list(self.config["output"]["columns"].keys())

            return ProcessingResult(
                success=True,
                data=result_df,
                processing_mode=ProcessingMode.STRICT,
                successful_columns=self.successful_columns,
                failed_columns=[],
                skipped_columns=[],
                error_log=[],
                processing_time=0,
                fallback_used=False,
            )
        except Exception as e:
            self.logger.log_column_error(
                "TRANSFORMATION", e, ErrorCategory.TRANSFORMATION_ERROR
            )
            raise

    def _process_partial_mode(
        self, df: pd.DataFrame, transformation_engine: Any
    ) -> ProcessingResult:
        """Process in partial mode - skip problematic columns."""
        result_df = df.copy()
        output_columns = self.config["output"]["columns"]

        # Get execution order from transformation engine
        try:
            execution_plan = transformation_engine.execution_engine.plan_execution(
                output_columns, set(df.columns)
            )
            execution_order = execution_plan["execution_order"]
        except Exception:
            execution_order = list(output_columns.keys())

        for column_name in execution_order:
            column_config = output_columns[column_name]

            try:
                start_time = time.time()
                # Process individual column
                result_df[column_name] = transformation_engine._process_column(
                    result_df, column_name, column_config
                )

                processing_time = time.time() - start_time
                self.column_processing_times[column_name] = processing_time
                self.successful_columns.append(column_name)
                self.logger.log_column_success(column_name, processing_time)

            except Exception as e:
                # Categorize error
                category = self._categorize_error(e, column_config)

                # Extract affected indices if available
                indices = self._extract_error_indices(e)

                self.failed_columns.append(column_name)
                self.logger.log_column_error(
                    column_name, e, category, indices, skipped=True
                )

                # Apply fallback transformation if available
                if self._apply_column_fallback(result_df, column_name, column_config):
                    self.logger.logger.info(
                        f"🔄 Applied fallback transformation for '{column_name}'"
                    )

        # Check if we should activate full fallback
        failure_rate = len(self.failed_columns) / len(output_columns)
        if failure_rate > self.failure_threshold and self.enable_fallback:
            self.logger.log_fallback_activation(
                f"Failure rate {failure_rate:.1%} exceeds threshold {self.failure_threshold:.1%}"
            )
            return ProcessingResult(
                success=False,
                data=result_df,
                processing_mode=ProcessingMode.PARTIAL,
                successful_columns=self.successful_columns,
                failed_columns=self.failed_columns,
                skipped_columns=self.skipped_columns,
                error_log=self.logger.error_log,
                processing_time=0,
                fallback_used=True,
            )

        # Apply filters and sorting to successful columns
        result_df = self._apply_post_processing(result_df, transformation_engine)

        self.logger.log_partial_processing(self.successful_columns, self.failed_columns)

        return ProcessingResult(
            success=len(self.successful_columns) > 0,
            data=result_df,
            processing_mode=ProcessingMode.PARTIAL,
            successful_columns=self.successful_columns,
            failed_columns=self.failed_columns,
            skipped_columns=self.skipped_columns,
            error_log=self.logger.error_log,
            processing_time=0,
            fallback_used=False,
        )

    def _process_fallback_mode(
        self,
        df: pd.DataFrame,
        transformation_engine: Any,
        fallback_query_func: Optional[Callable] = None,
    ) -> ProcessingResult:
        """Process in fallback mode - use direct database query or basic transformations."""
        if fallback_query_func:
            try:
                self.logger.log_fallback_activation(
                    "Fallback mode explicitly requested"
                )
                fallback_df = fallback_query_func()
                return ProcessingResult(
                    success=True,
                    data=fallback_df,
                    processing_mode=ProcessingMode.FALLBACK,
                    successful_columns=[],
                    failed_columns=[],
                    skipped_columns=list(self.config["output"]["columns"].keys()),
                    error_log=[],
                    processing_time=0,
                    fallback_used=True,
                )
            except Exception as e:
                self.logger.log_column_error(
                    "FALLBACK_QUERY", e, ErrorCategory.SYSTEM_ERROR
                )

        # Apply basic transformations
        result_df = self._apply_basic_transformations(df)

        return ProcessingResult(
            success=True,
            data=result_df,
            processing_mode=ProcessingMode.FALLBACK,
            successful_columns=[],
            failed_columns=[],
            skipped_columns=list(self.config["output"]["columns"].keys()),
            error_log=[],
            processing_time=0,
            fallback_used=True,
        )

    def _categorize_error(
        self, error: Exception, column_config: Dict[str, Any]
    ) -> ErrorCategory:
        """Categorize error type for better debugging."""
        error_message = str(error).lower()
        error_type = type(error).__name__

        if (
            "validation" in error_message
            or "required" in error_message
            or "null" in error_message
        ):
            return ErrorCategory.VALIDATION_ERROR
        elif "transformation" in error_message or "expression" in error_message:
            return ErrorCategory.TRANSFORMATION_ERROR
        elif (
            "type" in error_message
            or "conversion" in error_message
            or "convert" in error_message
            or error_type == "TypeError"
        ):
            return ErrorCategory.DATA_TYPE_ERROR
        elif "dependency" in error_message or "not found" in error_message:
            return ErrorCategory.DEPENDENCY_ERROR
        elif "config" in error_message:
            return ErrorCategory.CONFIGURATION_ERROR
        elif error_type in ["FileNotFoundError", "ConnectionError", "IOError"]:
            return ErrorCategory.INPUT_ERROR
        else:
            return ErrorCategory.SYSTEM_ERROR

    def _extract_error_indices(self, error: Exception) -> Optional[List[int]]:
        """Extract affected row indices from error message."""
        error_message = str(error)

        # Look for patterns like "at indices: [1, 2, 3]"
        import re

        indices_match = re.search(r"at indices: \[([^\]]+)\]", error_message)
        if indices_match:
            try:
                indices_str = indices_match.group(1)
                indices = [int(x.strip()) for x in indices_str.split(",")]
                return indices
            except ValueError:
                pass

        return None

    def _apply_column_fallback(
        self, df: pd.DataFrame, column_name: str, column_config: Dict[str, Any]
    ) -> bool:
        """Apply fallback transformation for a specific column."""
        fallback_config = self.fallback_transformations.get(column_name)
        if not fallback_config:
            return False

        try:
            if fallback_config["type"] == "default_value":
                df[column_name] = fallback_config["value"]
            elif fallback_config["type"] == "copy_column":
                source_col = fallback_config["source"]
                if source_col in df.columns:
                    df[column_name] = df[source_col]
                else:
                    return False
            elif fallback_config["type"] == "basic_calculation":
                # Simple calculations like mean, median, etc.
                operation = fallback_config["operation"]
                source_col = fallback_config["source"]
                if source_col in df.columns:
                    if operation == "mean":
                        df[column_name] = df[source_col].mean()
                    elif operation == "median":
                        df[column_name] = df[source_col].median()
                    elif operation == "forward_fill":
                        df[column_name] = df[source_col].fillna(method="ffill")
                    else:
                        return False
                else:
                    return False

            return True
        except Exception:
            return False

    def _apply_basic_transformations(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply basic transformations when full processing fails."""
        result_df = df.copy()

        # Apply basic column mappings and type conversions
        output_columns = self.config["output"]["columns"]

        for column_name, column_config in output_columns.items():
            try:
                # Simple source mapping
                source = column_config.get("source", column_name)
                if source in df.columns:
                    result_df[column_name] = df[source]

                    # Basic type conversion
                    target_type = column_config.get("type", "string")
                    if target_type == "float":
                        result_df[column_name] = pd.to_numeric(
                            result_df[column_name], errors="coerce"
                        )
                    elif target_type == "int":
                        result_df[column_name] = pd.to_numeric(
                            result_df[column_name], errors="coerce"
                        ).astype("Int64")
                    elif target_type == "datetime":
                        result_df[column_name] = pd.to_datetime(
                            result_df[column_name], errors="coerce"
                        )

            except Exception:
                # Skip problematic columns in basic mode
                continue

        return result_df

    def _apply_post_processing(
        self, df: pd.DataFrame, transformation_engine: Any
    ) -> pd.DataFrame:
        """Apply filters and sorting to the DataFrame."""
        try:
            # Apply filters if they exist and don't reference failed columns
            if "filters" in self.config["output"]:
                df = transformation_engine._apply_filters(df)
        except Exception as e:
            self.logger.log_column_error(
                "FILTERS", e, ErrorCategory.TRANSFORMATION_ERROR
            )

        try:
            # Apply sorting if it exists and columns are available
            if "sort" in self.config["output"]:
                df = transformation_engine._apply_sorting(df)
        except Exception as e:
            self.logger.log_column_error(
                "SORTING", e, ErrorCategory.TRANSFORMATION_ERROR
            )

        return df

    def get_processing_recommendations(self) -> List[str]:
        """Get recommendations for improving processing success."""
        recommendations = []

        if not self.failed_columns:
            recommendations.append("✅ All columns processed successfully!")
            return recommendations

        failure_rate = len(self.failed_columns) / (
            len(self.successful_columns) + len(self.failed_columns)
        )

        if failure_rate > 0.5:
            recommendations.append("🚨 High failure rate detected:")
            recommendations.append("  - Consider enabling partial processing mode")
            recommendations.append("  - Review configuration for common patterns")
            recommendations.append("  - Test with smaller dataset first")

        if self.failed_columns:
            recommendations.append("🔧 For failed columns:")
            recommendations.append(
                "  - Add fallback transformations in global_settings"
            )
            recommendations.append("  - Consider making validations less strict")
            recommendations.append("  - Check data quality at source")

        # Add specific recommendations based on error patterns
        recommendations.extend(self.logger.get_debugging_suggestions())

        return recommendations
