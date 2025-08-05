"""Enhanced logging for DataTidy with error categorization and detailed reporting."""

import logging
import json
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum

# import pandas as pd  # Unused


class ErrorCategory(Enum):
    """Categories of errors for better debugging."""

    VALIDATION_ERROR = "validation_error"
    TRANSFORMATION_ERROR = "transformation_error"
    DATA_TYPE_ERROR = "data_type_error"
    DEPENDENCY_ERROR = "dependency_error"
    CONFIGURATION_ERROR = "configuration_error"
    INPUT_ERROR = "input_error"
    SYSTEM_ERROR = "system_error"


class ProcessingMode(Enum):
    """Processing modes for DataTidy."""

    STRICT = "strict"
    PARTIAL = "partial"
    FALLBACK = "fallback"


class EnhancedLogger:
    """Enhanced logger with detailed error categorization and metrics."""

    def __init__(self, name: str = "datatidy", log_level: int = logging.INFO):
        """Initialize enhanced logger."""
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)

        # Create formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        # Create console handler if not exists
        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

        # Track errors and metrics
        self.error_log: List[Dict[str, Any]] = []
        self.processing_metrics: Dict[str, Any] = {
            "start_time": None,
            "end_time": None,
            "processing_mode": None,
            "total_columns": 0,
            "successful_columns": 0,
            "failed_columns": 0,
            "skipped_columns": 0,
            "fallback_used": False,
            "error_categories": {},
        }

    def start_processing(self, mode: ProcessingMode, total_columns: int):
        """Log start of processing."""
        self.processing_metrics["start_time"] = datetime.now()
        self.processing_metrics["processing_mode"] = mode.value
        self.processing_metrics["total_columns"] = total_columns

        self.logger.info(f"🔄 Starting DataTidy processing in {mode.value} mode")
        self.logger.info(f"📊 Processing {total_columns} columns")

    def log_column_success(self, column_name: str, processing_time: float = None):
        """Log successful column processing."""
        self.processing_metrics["successful_columns"] += 1

        if processing_time:
            self.logger.debug(
                f"✅ Column '{column_name}' processed successfully ({processing_time:.3f}s)"
            )
        else:
            self.logger.debug(f"✅ Column '{column_name}' processed successfully")

    def log_column_error(
        self,
        column_name: str,
        error: Exception,
        category: ErrorCategory,
        indices: Optional[List[int]] = None,
        skipped: bool = False,
    ):
        """Log column processing error with categorization."""
        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "column": column_name,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "category": category.value,
            "indices": (
                indices[:10] if indices and len(indices) > 10 else indices
            ),  # Limit to first 10
            "total_affected_rows": len(indices) if indices else None,
            "skipped": skipped,
        }

        self.error_log.append(error_entry)

        # Update metrics
        if skipped:
            self.processing_metrics["skipped_columns"] += 1
        else:
            self.processing_metrics["failed_columns"] += 1

        # Update error category counts
        if category.value not in self.processing_metrics["error_categories"]:
            self.processing_metrics["error_categories"][category.value] = 0
        self.processing_metrics["error_categories"][category.value] += 1

        # Log error
        if indices:
            affected_info = f" (affecting {len(indices)} rows)"
            if len(indices) <= 5:
                affected_info += f" at indices: {indices}"
            else:
                affected_info += (
                    f" at indices: {indices[:5]}... and {len(indices)-5} more"
                )
        else:
            affected_info = ""

        action = "⏭️  Skipped" if skipped else "❌ Failed"
        self.logger.warning(f"{action} column '{column_name}': {error}{affected_info}")

    def log_fallback_activation(self, reason: str):
        """Log fallback mode activation."""
        self.processing_metrics["fallback_used"] = True
        self.logger.warning(f"🔄 Fallback mode activated: {reason}")

    def log_partial_processing(
        self, successful_columns: List[str], failed_columns: List[str]
    ):
        """Log partial processing results."""
        self.logger.info("🎯 Partial processing completed:")
        self.logger.info(f"   ✅ {len(successful_columns)} columns successful")
        self.logger.info(f"   ❌ {len(failed_columns)} columns failed")

        if failed_columns:
            self.logger.info(f"   Failed columns: {', '.join(failed_columns)}")

    def end_processing(self, success: bool = True):
        """Log end of processing with summary."""
        self.processing_metrics["end_time"] = datetime.now()

        if self.processing_metrics["start_time"]:
            duration = (
                self.processing_metrics["end_time"]
                - self.processing_metrics["start_time"]
            )
            duration_str = f"({duration.total_seconds():.2f}s)"
        else:
            duration_str = ""

        if success:
            self.logger.info(
                f"✅ DataTidy processing completed successfully {duration_str}"
            )
        else:
            self.logger.error(f"❌ DataTidy processing failed {duration_str}")

        self._log_processing_summary()

    def _log_processing_summary(self):
        """Log detailed processing summary."""
        metrics = self.processing_metrics

        self.logger.info("📊 Processing Summary:")
        self.logger.info(f"   Mode: {metrics['processing_mode']}")
        self.logger.info(f"   Total columns: {metrics['total_columns']}")
        self.logger.info(f"   Successful: {metrics['successful_columns']}")
        self.logger.info(f"   Failed: {metrics['failed_columns']}")
        self.logger.info(f"   Skipped: {metrics['skipped_columns']}")

        if metrics["fallback_used"]:
            self.logger.info("   🔄 Fallback processing was used")

        if metrics["error_categories"]:
            self.logger.info("   Error breakdown:")
            for category, count in metrics["error_categories"].items():
                self.logger.info(f"     {category}: {count}")

    def get_error_report(self) -> Dict[str, Any]:
        """Get detailed error report."""
        return {
            "processing_metrics": self.processing_metrics,
            "error_log": self.error_log,
            "error_summary": self._generate_error_summary(),
        }

    def _generate_error_summary(self) -> Dict[str, Any]:
        """Generate error summary for debugging."""
        if not self.error_log:
            return {"total_errors": 0}

        summary = {
            "total_errors": len(self.error_log),
            "by_category": {},
            "by_column": {},
            "most_common_errors": {},
        }

        # Group by category
        for error in self.error_log:
            category = error["category"]
            column = error["column"]
            error_type = error["error_type"]

            # By category
            if category not in summary["by_category"]:
                summary["by_category"][category] = 0
            summary["by_category"][category] += 1

            # By column
            if column not in summary["by_column"]:
                summary["by_column"][column] = 0
            summary["by_column"][column] += 1

            # By error type
            if error_type not in summary["most_common_errors"]:
                summary["most_common_errors"][error_type] = 0
            summary["most_common_errors"][error_type] += 1

        return summary

    def export_error_log(self, file_path: str):
        """Export error log to JSON file."""
        report = self.get_error_report()

        with open(file_path, "w") as f:
            json.dump(report, f, indent=2, default=str)

        self.logger.info(f"📁 Error report exported to: {file_path}")

    def get_debugging_suggestions(self) -> List[str]:
        """Get suggestions for debugging based on error patterns."""
        suggestions = []

        if not self.error_log:
            return ["✅ No errors found - configuration looks good!"]

        error_categories = self.processing_metrics.get("error_categories", {})

        # Validation error suggestions
        if ErrorCategory.VALIDATION_ERROR.value in error_categories:
            suggestions.append("🔍 Validation errors detected:")
            suggestions.append("  - Check data types and null value handling")
            suggestions.append(
                "  - Consider using 'nullable: true' or providing default values"
            )
            suggestions.append("  - Review min/max value constraints")

        # Transformation error suggestions
        if ErrorCategory.TRANSFORMATION_ERROR.value in error_categories:
            suggestions.append("🔧 Transformation errors detected:")
            suggestions.append("  - Check transformation expressions for syntax errors")
            suggestions.append("  - Verify that referenced columns exist")
            suggestions.append(
                "  - Consider using conditional logic to handle edge cases"
            )

        # Dependency error suggestions
        if ErrorCategory.DEPENDENCY_ERROR.value in error_categories:
            suggestions.append("🔗 Dependency errors detected:")
            suggestions.append("  - Check column dependency order")
            suggestions.append("  - Ensure all referenced columns are defined")
            suggestions.append(
                "  - Consider using interim columns for complex dependencies"
            )

        # High failure rate suggestions
        failure_rate = self.processing_metrics["failed_columns"] / max(
            1, self.processing_metrics["total_columns"]
        )
        if failure_rate > 0.5:
            suggestions.append("⚠️  High failure rate detected:")
            suggestions.append("  - Consider enabling partial processing mode")
            suggestions.append("  - Review configuration for common issues")
            suggestions.append("  - Test with a smaller dataset first")

        return suggestions
