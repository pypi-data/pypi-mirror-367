"""Examples demonstrating dependency-aware column processing using separate YAML files."""

import pandas as pd
import numpy as np
from datatidy import DataTidy


def create_sample_sales_data():
    """Create sample sales data for dependency examples."""
    np.random.seed(42)

    products = [
        "Laptop",
        "Mouse",
        "Keyboard",
        "Monitor",
        "Tablet",
        "Phone",
        "Headphones",
        "Camera",
    ]
    categories = [
        "Electronics",
        "Electronics",
        "Electronics",
        "Electronics",
        "Electronics",
        "Electronics",
        "Electronics",
        "Electronics",
    ]
    regions = ["North", "South", "East", "West"]

    data = []
    for i in range(100):
        product_idx = np.random.randint(0, len(products))
        data.append(
            {
                "id": i + 1,
                "product": products[product_idx],
                "price": np.random.uniform(50, 800),
                "quantity": np.random.randint(1, 150),
                "category": categories[product_idx],
                "region": np.random.choice(regions),
                "date": pd.date_range("2023-01-01", periods=365, freq="D")[
                    np.random.randint(0, 365)
                ].strftime("%Y-%m-%d"),
            }
        )

    df = pd.DataFrame(data)
    df.to_csv("examples/sales_data.csv", index=False)
    print("Sample sales data created: sales_data.csv")
    return df


def example_basic_dependencies():
    """Demonstrate basic dependency resolution using YAML config."""
    print("=== BASIC DEPENDENCY RESOLUTION ===")
    print("Using configuration: basic_dependency_example.yaml")

    create_sample_sales_data()

    # Load configuration from YAML file
    dt = DataTidy("examples/basic_dependency_example.yaml")
    result = dt.process_data()

    print("Results with dependency resolution:")
    print(result[["product", "price", "quantity", "revenue", "sales_category"]].head())
    print("Note: 'total_sales' is interim and not in final output")
    print()


def example_complex_dependencies():
    """Demonstrate complex multi-level dependencies using YAML config."""
    print("=== COMPLEX MULTI-LEVEL DEPENDENCIES ===")
    print("Using configuration: complex_dependency_example.yaml")

    # Load configuration from YAML file
    dt = DataTidy("examples/complex_dependency_example.yaml")
    result = dt.process_data()

    print("Complex dependency resolution result:")
    print(result[["final_rating", "recommendation"]].head())
    print()


def example_circular_dependency_error():
    """Demonstrate circular dependency detection using YAML config."""
    print("=== CIRCULAR DEPENDENCY DETECTION ===")
    print("Using configuration: circular_dependency_example.yaml")

    # Load configuration from YAML file that has circular dependencies
    dt = DataTidy("examples/circular_dependency_example.yaml")

    try:
        result = dt.process_data()
        print("ERROR: Should have detected circular dependency!")
    except Exception as e:
        print(f"✓ Correctly detected circular dependency: {e}")
    print()


def example_filter_with_interim_columns():
    """Demonstrate using interim columns in filters using YAML config."""
    print("=== FILTERS WITH INTERIM COLUMNS ===")
    print("Using configuration: interim_columns_filter_example.yaml")

    # Load configuration from YAML file
    dt = DataTidy("examples/interim_columns_filter_example.yaml")
    result = dt.process_data()

    print("Filtered results (total_value > 500 AND profit_estimate > 50):")
    print(
        result[
            [
                "product",
                "price",
                "quantity",
                "high_value_product",
                "value_category",
                "profitability_tier",
            ]
        ].head()
    )
    print(f"Original data: 100 rows, Filtered data: {len(result)} rows")
    print(
        "Note: 'total_value' and 'profit_estimate' interim columns were used for filtering but not included in output"
    )
    print()


def example_execution_plan_debugging():
    """Demonstrate execution plan debugging features using YAML config."""
    print("=== EXECUTION PLAN DEBUGGING ===")
    print("Using configuration: execution_plan_debug_example.yaml")

    print("Processing with execution plan debugging enabled...")
    dt = DataTidy("examples/execution_plan_debug_example.yaml")
    result = dt.process_data()

    print("\nFinal result (only non-interim columns):")
    print(result[["product", "final_result", "summary"]].head())
    print()


def example_advanced_operations_with_dependencies():
    """Demonstrate advanced operations with dependencies using YAML config."""
    print("=== ADVANCED OPERATIONS WITH DEPENDENCIES ===")
    print("Using configuration: advanced_operations_dependency_example.yaml")

    # Load configuration from YAML file
    dt = DataTidy("examples/advanced_operations_dependency_example.yaml")
    result = dt.process_data()

    print("Advanced operations with dependency resolution:")
    print(
        result[
            ["product_summary", "performance_analysis", "recommendation_engine"]
        ].head()
    )
    print()


def run_all_examples():
    """Run all dependency examples using separate YAML configurations."""
    print("=== DEPENDENCY-AWARE COLUMN PROCESSING EXAMPLES ===")
    print("All examples use separate YAML configuration files\n")

    example_basic_dependencies()
    example_complex_dependencies()
    example_circular_dependency_error()
    example_filter_with_interim_columns()
    example_execution_plan_debugging()
    example_advanced_operations_with_dependencies()

    print("=== AVAILABLE YAML CONFIGURATION FILES ===")
    print("📁 examples/basic_dependency_example.yaml - Basic dependency resolution")
    print("📁 examples/complex_dependency_example.yaml - Multi-level dependencies")
    print(
        "📁 examples/circular_dependency_example.yaml - Circular dependency detection"
    )
    print(
        "📁 examples/interim_columns_filter_example.yaml - Interim columns in filters"
    )
    print("📁 examples/execution_plan_debug_example.yaml - Execution plan debugging")
    print(
        "📁 examples/advanced_operations_dependency_example.yaml - Advanced operations with dependencies"
    )
    print(
        "📁 examples/dependency_aware_config.yaml - Comprehensive example with all features"
    )
    print()

    print("=== SUMMARY ===")
    print("DataTidy's dependency-aware processing features:")
    print("✓ Automatic dependency resolution - define columns in any order")
    print("✓ Interim columns - create temporary columns for calculations")
    print("✓ Circular dependency detection - prevents infinite loops")
    print(
        "✓ Complex multi-level dependencies - columns can depend on other computed columns"
    )
    print("✓ Interim columns in filters - use temporary columns for row filtering")
    print("✓ Execution plan debugging - see exactly how columns are processed")
    print("✓ Safe execution - dependency validation before processing")
    print("✓ YAML-based configurations - clean separation of config and code")


if __name__ == "__main__":
    run_all_examples()
