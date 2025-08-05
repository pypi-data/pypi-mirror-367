"""Tests for fallback processing functionality."""

import pytest
import pandas as pd
import numpy as np
from datatidy.fallback.processor import FallbackProcessor, ProcessingResult
from datatidy.fallback.logger import EnhancedLogger, ErrorCategory, ProcessingMode
from datatidy.fallback.metrics import DataQualityMetrics
from datatidy.transformation.engine import TransformationEngine


class TestFallbackProcessor:
    """Test fallback processor functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.sample_config = {
            "output": {
                "columns": {
                    "id": {"source": "id", "type": "int"},
                    "name": {"source": "name", "type": "string"},
                    "processed_amount": {
                        "transformation": "amount * 1.1",
                        "type": "float",
                        "validation": {"min_value": 0},
                    },
                    "status": {
                        "source": "status",
                        "type": "string",
                        "validation": {"required": True},
                    },
                }
            },
            "global_settings": {
                "processing_mode": "partial",
                "enable_partial_processing": True,
                "enable_fallback": True,
                "max_column_failures": 5,
                "failure_threshold": 0.3,
                "fallback_transformations": {
                    "processed_amount": {"type": "copy_column", "source": "amount"}
                },
            },
        }

        self.sample_data = pd.DataFrame(
            {
                "id": [1, 2, 3, 4, 5],
                "name": ["Alice", "Bob", "Charlie", None, "Eve"],
                "amount": [100.0, 200.0, None, 400.0, 500.0],
                "status": ["active", "inactive", "pending", None, "active"],
            }
        )

    def test_partial_processing_mode(self):
        """Test partial processing mode with column failures."""
        logger = EnhancedLogger()
        processor = FallbackProcessor(self.sample_config, logger)

        # Mock transformation engine that fails on certain columns
        class MockTransformationEngine:
            def __init__(self):
                self.execution_engine = MockExecutionEngine()

            def _process_column(self, df, column_name, column_config):
                if column_name == "status" and "validation" in column_config:
                    # Simulate validation failure
                    raise ValueError(
                        "Required field 'status' has null values at indices: [3]"
                    )
                elif column_name == "processed_amount":
                    # Simulate transformation with null handling
                    return df["amount"] * 1.1
                else:
                    return df[column_config.get("source", column_name)]

            def _apply_filters(self, df):
                return df

            def _apply_sorting(self, df):
                return df

        class MockExecutionEngine:
            def plan_execution(self, output_columns, input_columns):
                return {
                    "execution_order": list(output_columns.keys()),
                    "final_columns": list(output_columns.keys()),
                    "interim_columns": [],
                }

        engine = MockTransformationEngine()
        result = processor.process_with_fallback(self.sample_data, engine)

        assert result.processing_mode == ProcessingMode.PARTIAL
        assert len(result.successful_columns) > 0
        assert len(result.failed_columns) > 0
        assert "status" in result.failed_columns

    def test_strict_mode_failure(self):
        """Test strict mode fails on any error."""
        config = self.sample_config.copy()
        config["global_settings"]["processing_mode"] = "strict"

        logger = EnhancedLogger()
        processor = FallbackProcessor(config, logger)

        class MockTransformationEngine:
            def transform(self, df):
                raise ValueError("Transformation failed")

        engine = MockTransformationEngine()
        result = processor.process_with_fallback(self.sample_data, engine)

        assert not result.success
        assert result.processing_mode == ProcessingMode.STRICT

    def test_fallback_mode_with_query_function(self):
        """Test fallback mode with external query function."""
        config = self.sample_config.copy()
        config["global_settings"]["processing_mode"] = "fallback"

        logger = EnhancedLogger()
        processor = FallbackProcessor(config, logger)

        def mock_fallback_query():
            return pd.DataFrame(
                {
                    "id": [1, 2, 3],
                    "name": ["Test1", "Test2", "Test3"],
                    "amount": [100, 200, 300],
                }
            )

        class MockTransformationEngine:
            pass

        engine = MockTransformationEngine()
        result = processor.process_with_fallback(
            self.sample_data, engine, mock_fallback_query
        )

        assert result.success
        assert result.fallback_used
        assert len(result.data) == 3


class TestEnhancedLogger:
    """Test enhanced logging functionality."""

    def test_error_categorization(self):
        """Test error categorization logic."""
        logger = EnhancedLogger()

        # Test different error types
        validation_error = ValueError("Required field 'name' has null values")
        transformation_error = ValueError("Transformation expression failed")
        type_error = TypeError("Cannot convert string to float")

        from datatidy.fallback.processor import FallbackProcessor

        processor = FallbackProcessor({}, logger)

        val_category = processor._categorize_error(validation_error, {})
        trans_category = processor._categorize_error(transformation_error, {})
        type_category = processor._categorize_error(type_error, {})

        assert val_category == ErrorCategory.VALIDATION_ERROR
        assert trans_category == ErrorCategory.TRANSFORMATION_ERROR
        assert type_category == ErrorCategory.DATA_TYPE_ERROR

    def test_processing_metrics(self):
        """Test processing metrics tracking."""
        logger = EnhancedLogger()

        logger.start_processing(ProcessingMode.PARTIAL, 5)
        logger.log_column_success("col1", 0.1)
        logger.log_column_success("col2", 0.2)
        logger.log_column_error(
            "col3", ValueError("Test error"), ErrorCategory.VALIDATION_ERROR
        )
        logger.end_processing(success=True)

        metrics = logger.processing_metrics
        assert metrics["total_columns"] == 5
        assert metrics["successful_columns"] == 2
        assert metrics["failed_columns"] == 1
        assert metrics["processing_mode"] == "partial"

    def test_debugging_suggestions(self):
        """Test debugging suggestions generation."""
        logger = EnhancedLogger()

        # Log some errors
        logger.log_column_error(
            "col1",
            ValueError("Required field has null values"),
            ErrorCategory.VALIDATION_ERROR,
        )
        logger.log_column_error(
            "col2",
            ValueError("Transformation failed"),
            ErrorCategory.TRANSFORMATION_ERROR,
        )

        suggestions = logger.get_debugging_suggestions()
        assert len(suggestions) > 0
        assert any("validation" in s.lower() for s in suggestions)
        assert any("transformation" in s.lower() for s in suggestions)


class TestDataQualityMetrics:
    """Test data quality metrics and comparison."""

    def test_column_metrics_calculation(self):
        """Test calculation of column-level metrics."""
        datatidy_series = pd.Series([1, 2, 3, None, 5])
        fallback_series = pd.Series([1, 2, 3, 4, 5])

        metrics = DataQualityMetrics._calculate_column_metrics(
            datatidy_series, fallback_series, "test_column"
        )

        assert metrics.column_name == "test_column"
        assert metrics.datatidy_nulls == 1
        assert metrics.fallback_nulls == 0
        assert metrics.completeness_diff < 0  # DataTidy has more nulls

    def test_data_comparison(self):
        """Test full data comparison between DataTidy and fallback results."""
        datatidy_df = pd.DataFrame(
            {
                "id": [1, 2, 3],
                "amount": [100.0, None, 300.0],
                "processed": [110.0, 220.0, 330.0],
            }
        )

        fallback_df = pd.DataFrame(
            {
                "id": [1, 2, 3],
                "amount": [100.0, 200.0, 300.0],
                "status": ["active", "inactive", "pending"],
            }
        )

        comparison = DataQualityMetrics.compare_results(
            datatidy_df, fallback_df, 1.5, 0.8
        )

        assert comparison.datatidy_rows == 3
        assert comparison.fallback_rows == 3
        assert len(comparison.common_columns) == 2  # id, amount
        assert "processed" in comparison.datatidy_only_columns
        assert "status" in comparison.fallback_only_columns
        assert comparison.processing_time_comparison["ratio"] > 1  # DataTidy slower

    def test_quality_score_calculation(self):
        """Test quality score calculation logic."""
        # Perfect match case
        score_perfect = DataQualityMetrics._calculate_quality_score(0.0, 0.0, True)
        assert score_perfect == 1.0

        # Worse completeness case
        score_worse = DataQualityMetrics._calculate_quality_score(-0.2, 0.0, True)
        assert score_worse < 1.0

        # Type mismatch case
        score_mismatch = DataQualityMetrics._calculate_quality_score(0.0, 0.0, False)
        assert score_mismatch < 1.0

    def test_recommendations_generation(self):
        """Test recommendations generation based on quality metrics."""
        # Create mock comparison with issues
        from datatidy.fallback.metrics import ColumnMetrics, DataQualityComparison

        low_quality_metric = ColumnMetrics(
            column_name="problem_col",
            datatidy_count=100,
            fallback_count=100,
            datatidy_nulls=50,
            fallback_nulls=10,
            datatidy_uniques=20,
            fallback_uniques=25,
            data_type_match=False,
            completeness_diff=-0.4,
            uniqueness_diff=-0.05,
            quality_score=0.3,
        )

        recommendations = DataQualityMetrics._generate_recommendations(
            pd.DataFrame({"col": [1, 2]}),
            pd.DataFrame({"col": [1, 2, 3]}),
            [low_quality_metric],
            2.0,
            0.5,
        )

        assert len(recommendations) > 0
        assert any("quality" in rec.lower() for rec in recommendations)


class TestIntegration:
    """Integration tests for the complete fallback system."""

    def test_end_to_end_partial_processing(self):
        """Test end-to-end partial processing with real DataTidy components."""
        config = {
            "output": {
                "columns": {
                    "id": {"source": "id", "type": "int"},
                    "doubled": {"transformation": "value * 2", "type": "float"},
                    "validated": {
                        "source": "status",
                        "transformation": "nonexistent_column * 2",  # This will fail
                        "type": "string",
                    },
                }
            },
            "global_settings": {
                "processing_mode": "partial",
                "enable_partial_processing": True,
                "ignore_errors": False,
            },
        }

        data = pd.DataFrame(
            {
                "id": [1, 2, 3],
                "value": [10, 20, 30],
                "status": ["ok", None, "pending"],  # This will cause validation to fail
            }
        )

        logger = EnhancedLogger()
        processor = FallbackProcessor(config, logger)
        engine = TransformationEngine(config)

        result = processor.process_with_fallback(data, engine)

        # Should have partial success
        assert result.processing_mode == ProcessingMode.PARTIAL
        assert (
            len(result.successful_columns) >= 1
        )  # At least some columns should succeed
        assert len(result.failed_columns) >= 1  # validation should fail

    def test_error_extraction_from_messages(self):
        """Test extraction of row indices from error messages."""
        from datatidy.fallback.processor import FallbackProcessor

        processor = FallbackProcessor({}, EnhancedLogger())

        # Test error message with indices
        error_msg = "Required field 'status' has null values at indices: [1, 3, 5]"
        error = ValueError(error_msg)

        indices = processor._extract_error_indices(error)
        assert indices == [1, 3, 5]

        # Test error message without indices
        error_no_indices = ValueError("General transformation error")
        indices_none = processor._extract_error_indices(error_no_indices)
        assert indices_none is None


if __name__ == "__main__":
    pytest.main([__file__])
