#!/usr/bin/env python3
"""
Demo script showing DataTidy's enhanced fallback processing capabilities.

This script demonstrates:
1. Partial processing mode
2. Enhanced error logging and categorization
3. Data quality comparison
4. Processing recommendations
5. Fallback query integration

Run with: python examples/fallback_demo.py
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add the parent directory to the path to import datatidy
sys.path.insert(0, str(Path(__file__).parent.parent))

from datatidy import DataTidy
from datatidy.fallback.metrics import DataQualityMetrics


def create_sample_data():
    """Create sample data with various data quality issues."""
    np.random.seed(42)

    data = pd.DataFrame(
        {
            "id": range(1, 101),
            "name": [
                f"Facility_{i}" if i % 10 != 0 else None for i in range(1, 101)
            ],  # 10% nulls
            "debt_to_income": np.random.normal(2.5, 1.0, 100),
            "leverage_ratio": np.random.normal(1.8, 0.5, 100),
            "existing_risk_level": np.random.choice(["LOW", "MEDIUM", "HIGH"], 100),
            "amount": np.random.normal(1000000, 500000, 100),
        }
    )

    # Introduce some problematic values
    data.loc[data.index % 15 == 0, "debt_to_income"] = None  # More nulls
    data.loc[data.index % 20 == 0, "leverage_ratio"] = None  # More nulls
    data.loc[data.index < 5, "amount"] = -100000  # Negative values

    return data


def create_problematic_config():
    """Create a configuration that will have some failures."""
    return {
        "output": {
            "columns": {
                "facility_id": {
                    "source": "id",
                    "type": "int",
                    "validation": {"required": True},
                },
                "facility_name": {
                    "source": "name",
                    "type": "string",
                    "validation": {"required": True},  # This will fail due to nulls
                },
                "cash_flow_leverage": {
                    "transformation": "debt_to_income * leverage_ratio",
                    "type": "float",
                    "validation": {
                        "required": True,  # This will fail due to nulls
                        "min_value": 0,
                        "max_value": 20,
                    },
                },
                "risk_category": {
                    "transformation": "np.where(cash_flow_leverage > 5, 'HIGH', np.where(cash_flow_leverage > 2, 'MEDIUM', 'LOW'))",
                    "type": "string",
                    "validation": {"allowed_values": ["LOW", "MEDIUM", "HIGH"]},
                },
                "processed_amount": {
                    "transformation": "amount * 1.1",
                    "type": "float",
                    "validation": {
                        "min_value": 0
                    },  # This will fail for negative amounts
                },
            }
        },
        "global_settings": {
            "processing_mode": "partial",
            "enable_partial_processing": True,
            "enable_fallback": True,
            "max_column_failures": 10,
            "failure_threshold": 0.4,
            "fallback_transformations": {
                "facility_name": {"type": "default_value", "value": "Unknown Facility"},
                "cash_flow_leverage": {
                    "type": "basic_calculation",
                    "operation": "mean",
                    "source": "debt_to_income",
                },
                "processed_amount": {"type": "copy_column", "source": "amount"},
            },
            "verbose": True,
        },
    }


def fallback_database_query():
    """Simulate a fallback database query."""
    print("🔄 Executing fallback database query...")

    # Simulate cleaner data from database
    return pd.DataFrame(
        {
            "facility_id": range(1, 101),
            "facility_name": [f"DB_Facility_{i}" for i in range(1, 101)],
            "risk_level": np.random.choice(["LOW", "MEDIUM", "HIGH"], 100),
            "total_amount": np.random.normal(1000000, 300000, 100),
        }
    )


def main():
    """Run the fallback processing demo."""
    print("=" * 60)
    print("🚀 DataTidy Fallback Processing Demo")
    print("=" * 60)

    # Create sample data with quality issues
    print("\n📊 Creating sample data with quality issues...")
    sample_data = create_sample_data()
    print(f"Created dataset with {len(sample_data)} rows")
    print(f"Null values per column:")
    for col, nulls in sample_data.isnull().sum().items():
        if nulls > 0:
            print(f"  {col}: {nulls} nulls ({nulls/len(sample_data)*100:.1f}%)")

    # Create configuration with potential issues
    config = create_problematic_config()

    # Initialize DataTidy
    print("\n🔧 Initializing DataTidy with problematic configuration...")
    dt = DataTidy()
    dt.load_config_from_string("# Loaded from dict")
    dt.config = config
    dt.logger = dt.logger or dt.EnhancedLogger()
    dt.fallback_processor = dt.FallbackProcessor(config, dt.logger)
    dt.transformation_engine = dt.TransformationEngine(config)

    # Demo 1: Strict mode (will fail)
    print("\n" + "=" * 50)
    print("📋 DEMO 1: Strict Mode Processing")
    print("=" * 50)

    dt.set_processing_mode("strict")
    try:
        result_strict = dt.process_data_with_fallback(sample_data)
        print("✅ Strict mode succeeded (unexpected!)")
    except Exception as e:
        print(f"❌ Strict mode failed as expected: {str(e)[:100]}...")

    # Demo 2: Partial mode
    print("\n" + "=" * 50)
    print("📋 DEMO 2: Partial Mode Processing")
    print("=" * 50)

    dt.set_processing_mode("partial")
    result_partial = dt.process_data_with_fallback(sample_data)

    print(f"\n📈 Processing Results:")
    print(f"   Success: {'✅' if result_partial.success else '❌'}")
    print(f"   Successful columns: {len(result_partial.successful_columns)}")
    print(f"   Failed columns: {len(result_partial.failed_columns)}")
    print(f"   Error count: {len(result_partial.error_log)}")

    if result_partial.successful_columns:
        print(f"   ✅ Successful: {', '.join(result_partial.successful_columns)}")
    if result_partial.failed_columns:
        print(f"   ❌ Failed: {', '.join(result_partial.failed_columns)}")

    # Show error details
    if result_partial.error_log:
        print(f"\n⚠️  Error Details (showing first 3):")
        for i, error in enumerate(result_partial.error_log[:3]):
            print(f"   {i+1}. {error['column']}: {error['error_message']}")

    # Show recommendations
    print(f"\n💡 Processing Recommendations:")
    recommendations = dt.get_processing_recommendations()
    for rec in recommendations[:5]:
        print(f"   {rec}")

    # Demo 3: Fallback mode with external query
    print("\n" + "=" * 50)
    print("📋 DEMO 3: Fallback Mode with External Query")
    print("=" * 50)

    dt.set_processing_mode("fallback")
    result_fallback = dt.process_data_with_fallback(
        sample_data, fallback_query_func=fallback_database_query
    )

    print(f"\n📈 Fallback Results:")
    print(f"   Success: {'✅' if result_fallback.success else '❌'}")
    print(f"   Fallback used: {'✅' if result_fallback.fallback_used else '❌'}")
    print(f"   Result shape: {result_fallback.data.shape}")
    print(f"   Columns: {list(result_fallback.data.columns)}")

    # Demo 4: Data Quality Comparison
    if result_partial.success and result_fallback.success:
        print("\n" + "=" * 50)
        print("📋 DEMO 4: Data Quality Comparison")
        print("=" * 50)

        # Compare partial processing result with fallback
        comparison = DataQualityMetrics.compare_results(
            result_partial.data,
            result_fallback.data,
            result_partial.processing_time,
            result_fallback.processing_time,
        )

        DataQualityMetrics.print_comparison_summary(comparison)

    # Demo 5: Error Log Export
    print("\n" + "=" * 50)
    print("📋 DEMO 5: Error Log Export")
    print("=" * 50)

    error_file = "fallback_demo_errors.json"
    dt.export_error_log(error_file)
    print(f"📁 Error log exported to: {error_file}")

    # Show processing summary
    print("\n📊 Final Processing Summary:")
    summary = dt.get_processing_summary()
    for key, value in summary.items():
        print(f"   {key}: {value}")

    print("\n" + "=" * 60)
    print("✅ Fallback Processing Demo Complete!")
    print("=" * 60)
    print("\n💡 Key Benefits Demonstrated:")
    print("   • Graceful degradation when columns fail")
    print("   • Detailed error categorization and logging")
    print("   • Automatic fallback to database queries")
    print("   • Data quality comparison and metrics")
    print("   • Actionable recommendations for improvements")
    print("\n🎯 This ensures your applications maintain high availability")
    print("   while leveraging DataTidy's advanced processing when possible!")


if __name__ == "__main__":
    main()
