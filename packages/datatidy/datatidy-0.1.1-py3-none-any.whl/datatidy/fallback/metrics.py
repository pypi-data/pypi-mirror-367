"""Data quality metrics for comparing DataTidy vs fallback results."""

from typing import Dict, List, Any
import pandas as pd
import numpy as np
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ColumnMetrics:
    """Metrics for a single column comparison."""

    column_name: str
    datatidy_count: int
    fallback_count: int
    datatidy_nulls: int
    fallback_nulls: int
    datatidy_uniques: int
    fallback_uniques: int
    data_type_match: bool
    completeness_diff: float
    uniqueness_diff: float
    quality_score: float


@dataclass
class DataQualityComparison:
    """Complete comparison between DataTidy and fallback results."""

    datatidy_rows: int
    fallback_rows: int
    common_columns: List[str]
    datatidy_only_columns: List[str]
    fallback_only_columns: List[str]
    column_metrics: List[ColumnMetrics]
    overall_quality_score: float
    processing_time_comparison: Dict[str, float]
    recommendations: List[str]


class DataQualityMetrics:
    """Utility class for comparing data quality between processing modes."""

    @staticmethod
    def compare_results(
        datatidy_df: pd.DataFrame,
        fallback_df: pd.DataFrame,
        datatidy_time: float = 0,
        fallback_time: float = 0,
    ) -> DataQualityComparison:
        """
        Compare DataTidy results with fallback results.

        Args:
            datatidy_df: DataFrame from DataTidy processing
            fallback_df: DataFrame from fallback processing
            datatidy_time: Processing time for DataTidy
            fallback_time: Processing time for fallback

        Returns:
            DataQualityComparison object with detailed metrics
        """
        # Basic row and column analysis
        datatidy_cols = set(datatidy_df.columns)
        fallback_cols = set(fallback_df.columns)

        common_columns = list(datatidy_cols & fallback_cols)
        datatidy_only = list(datatidy_cols - fallback_cols)
        fallback_only = list(fallback_cols - datatidy_cols)

        # Calculate column-level metrics
        column_metrics = []
        quality_scores = []

        for col in common_columns:
            metrics = DataQualityMetrics._calculate_column_metrics(
                datatidy_df[col], fallback_df[col], col
            )
            column_metrics.append(metrics)
            quality_scores.append(metrics.quality_score)

        # Calculate overall quality score
        overall_score = np.mean(quality_scores) if quality_scores else 0.0

        # Generate recommendations
        recommendations = DataQualityMetrics._generate_recommendations(
            datatidy_df, fallback_df, column_metrics, datatidy_time, fallback_time
        )

        return DataQualityComparison(
            datatidy_rows=len(datatidy_df),
            fallback_rows=len(fallback_df),
            common_columns=common_columns,
            datatidy_only_columns=datatidy_only,
            fallback_only_columns=fallback_only,
            column_metrics=column_metrics,
            overall_quality_score=float(overall_score),
            processing_time_comparison={
                "datatidy": datatidy_time,
                "fallback": fallback_time,
                "ratio": datatidy_time / max(fallback_time, 0.001),
            },
            recommendations=recommendations,
        )

    @staticmethod
    def _calculate_column_metrics(
        datatidy_series: pd.Series, fallback_series: pd.Series, column_name: str
    ) -> ColumnMetrics:
        """Calculate metrics for comparing a single column."""
        # Basic counts
        dt_count = len(datatidy_series)
        fb_count = len(fallback_series)

        # Null analysis
        dt_nulls = datatidy_series.isna().sum()
        fb_nulls = fallback_series.isna().sum()

        # Unique values
        dt_uniques = datatidy_series.nunique()
        fb_uniques = fallback_series.nunique()

        # Data type compatibility
        dt_type = str(datatidy_series.dtype)
        fb_type = str(fallback_series.dtype)
        type_match = DataQualityMetrics._are_types_compatible(dt_type, fb_type)

        # Calculate quality differences
        dt_completeness = 1 - (dt_nulls / max(dt_count, 1))
        fb_completeness = 1 - (fb_nulls / max(fb_count, 1))
        completeness_diff = dt_completeness - fb_completeness

        dt_uniqueness = dt_uniques / max(dt_count, 1)
        fb_uniqueness = fb_uniques / max(fb_count, 1)
        uniqueness_diff = dt_uniqueness - fb_uniqueness

        # Overall quality score for this column
        quality_score = DataQualityMetrics._calculate_quality_score(
            completeness_diff, uniqueness_diff, type_match
        )

        return ColumnMetrics(
            column_name=column_name,
            datatidy_count=dt_count,
            fallback_count=fb_count,
            datatidy_nulls=dt_nulls,
            fallback_nulls=fb_nulls,
            datatidy_uniques=dt_uniques,
            fallback_uniques=fb_uniques,
            data_type_match=type_match,
            completeness_diff=completeness_diff,
            uniqueness_diff=uniqueness_diff,
            quality_score=quality_score,
        )

    @staticmethod
    def _are_types_compatible(type1: str, type2: str) -> bool:
        """Check if two data types are compatible."""
        # Normalize type names
        numeric_types = {"int64", "int32", "float64", "float32", "Int64", "Float64"}
        string_types = {"object", "string", "category"}
        datetime_types = {"datetime64[ns]", "datetime64", "period"}

        def get_type_category(dtype_str):
            if any(nt in dtype_str for nt in numeric_types):
                return "numeric"
            elif any(st in dtype_str for st in string_types):
                return "string"
            elif any(dt in dtype_str for dt in datetime_types):
                return "datetime"
            else:
                return "other"

        return get_type_category(type1) == get_type_category(type2)

    @staticmethod
    def _calculate_quality_score(
        completeness_diff: float, uniqueness_diff: float, type_match: bool
    ) -> float:
        """Calculate a quality score for column comparison."""
        score = 0.0

        # Completeness component (40% weight)
        if abs(completeness_diff) <= 0.01:  # Perfect or near-perfect completeness
            score += 0.4
        elif completeness_diff >= 0:
            score += 0.4 * min(1.0, completeness_diff * 2 + 0.5)
        else:
            score += 0.4 * max(0.0, 0.5 + completeness_diff * 2)

        # Uniqueness component (30% weight)
        if abs(uniqueness_diff) <= 0.1:  # Similar uniqueness is good
            score += 0.3
        else:
            score += 0.3 * max(0.0, 1.0 - abs(uniqueness_diff))

        # Type compatibility (30% weight)
        if type_match:
            score += 0.3

        return score

    @staticmethod
    def _generate_recommendations(
        datatidy_df: pd.DataFrame,
        fallback_df: pd.DataFrame,
        column_metrics: List[ColumnMetrics],
        datatidy_time: float,
        fallback_time: float,
    ) -> List[str]:
        """Generate recommendations based on quality comparison."""
        recommendations = []

        if not column_metrics:
            recommendations.append("⚠️  No common columns found for comparison")
            return recommendations

        avg_quality = np.mean([cm.quality_score for cm in column_metrics])

        # Overall assessment
        if avg_quality >= 0.8:
            recommendations.append("✅ DataTidy processing shows high quality results")
        elif avg_quality >= 0.6:
            recommendations.append(
                "⚠️  DataTidy processing shows moderate quality - consider optimizations"
            )
        else:
            recommendations.append(
                "🚨 DataTidy processing quality is low - review configuration"
            )

        # Row count comparison
        row_diff = len(datatidy_df) - len(fallback_df)
        if abs(row_diff) > 0.05 * len(fallback_df):  # More than 5% difference
            if row_diff > 0:
                recommendations.append(
                    f"📊 DataTidy returned {row_diff} more rows - check filters"
                )
            else:
                recommendations.append(
                    f"📊 DataTidy returned {abs(row_diff)} fewer rows - check data loss"
                )

        # Column-specific recommendations
        low_quality_columns = [cm for cm in column_metrics if cm.quality_score < 0.5]
        if low_quality_columns:
            recommendations.append("🔍 Low quality columns detected:")
            for cm in low_quality_columns[:3]:  # Show top 3
                recommendations.append(
                    f"  - {cm.column_name}: Review transformation logic"
                )

        # Completeness issues
        completeness_issues = [
            cm for cm in column_metrics if cm.completeness_diff < -0.1
        ]
        if completeness_issues:
            recommendations.append("⚠️  Completeness issues found:")
            for cm in completeness_issues[:3]:
                recommendations.append(
                    f"  - {cm.column_name}: High null rate in DataTidy result"
                )

        # Type mismatch issues
        type_issues = [cm for cm in column_metrics if not cm.data_type_match]
        if type_issues:
            recommendations.append("🔧 Data type mismatches found:")
            for cm in type_issues[:3]:
                recommendations.append(
                    f"  - {cm.column_name}: Check type conversion logic"
                )

        # Performance comparison
        if datatidy_time > 0 and fallback_time > 0:
            time_ratio = datatidy_time / fallback_time
            if time_ratio > 5:
                recommendations.append(
                    f"⏱️  DataTidy is {time_ratio:.1f}x slower - consider optimization"
                )
            elif time_ratio < 0.5:
                recommendations.append(
                    "🚀 DataTidy is significantly faster while maintaining quality"
                )

        return recommendations

    @staticmethod
    def export_comparison_report(
        comparison: DataQualityComparison, file_path: str, include_details: bool = True
    ):
        """Export detailed comparison report to file."""
        report: Dict[str, Any] = {
            "comparison_timestamp": datetime.now().isoformat(),
            "summary": {
                "datatidy_rows": comparison.datatidy_rows,
                "fallback_rows": comparison.fallback_rows,
                "common_columns": len(comparison.common_columns),
                "overall_quality_score": comparison.overall_quality_score,
                "processing_time_ratio": comparison.processing_time_comparison.get(
                    "ratio", 0
                ),
            },
            "recommendations": comparison.recommendations,
        }

        if include_details:
            report["detailed_metrics"] = [
                {
                    "column": cm.column_name,
                    "quality_score": cm.quality_score,
                    "completeness_diff": cm.completeness_diff,
                    "uniqueness_diff": cm.uniqueness_diff,
                    "type_match": cm.data_type_match,
                    "datatidy_nulls": cm.datatidy_nulls,
                    "fallback_nulls": cm.fallback_nulls,
                }
                for cm in comparison.column_metrics
            ]

        import json

        with open(file_path, "w") as f:
            json.dump(report, f, indent=2, default=str)

    @staticmethod
    def print_comparison_summary(comparison: DataQualityComparison):
        """Print a formatted summary of the comparison."""
        print("=" * 60)
        print("📊 DATA QUALITY COMPARISON REPORT")
        print("=" * 60)

        print(
            f"📈 Rows: DataTidy {comparison.datatidy_rows:,} | Fallback {comparison.fallback_rows:,}"
        )
        print(f"📋 Common columns: {len(comparison.common_columns)}")

        if comparison.datatidy_only_columns:
            print(f"📊 DataTidy-only columns: {len(comparison.datatidy_only_columns)}")

        if comparison.fallback_only_columns:
            print(f"📊 Fallback-only columns: {len(comparison.fallback_only_columns)}")

        print(f"⭐ Overall quality score: {comparison.overall_quality_score:.2f}/1.00")

        # Processing time comparison
        time_comp = comparison.processing_time_comparison
        if time_comp["datatidy"] > 0 and time_comp["fallback"] > 0:
            print(
                f"⏱️  Processing time: DataTidy {time_comp['datatidy']:.2f}s | "
                f"Fallback {time_comp['fallback']:.2f}s (ratio: {time_comp['ratio']:.1f}x)"
            )

        print("\n🔍 TOP COLUMN METRICS:")
        sorted_metrics = sorted(
            comparison.column_metrics, key=lambda x: x.quality_score, reverse=True
        )
        for i, cm in enumerate(sorted_metrics[:5]):
            status = (
                "✅"
                if cm.quality_score >= 0.8
                else "⚠️" if cm.quality_score >= 0.6 else "❌"
            )
            print(
                f"  {status} {cm.column_name}: {cm.quality_score:.2f} "
                f"(completeness: {cm.completeness_diff:+.2f}, type_match: {cm.data_type_match})"
            )

        print("\n💡 RECOMMENDATIONS:")
        for rec in comparison.recommendations:
            print(f"  {rec}")

        print("=" * 60)
