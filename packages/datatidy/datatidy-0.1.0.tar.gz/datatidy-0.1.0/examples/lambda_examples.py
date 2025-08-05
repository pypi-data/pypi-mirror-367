"""Examples demonstrating advanced column operations with lambda functions."""

import pandas as pd
from datatidy import DataTidy
import numpy as np


def create_sample_data():
    """Create sample data for advanced operations."""
    np.random.seed(42)

    data = {
        "id": range(1, 21),
        "text": [
            "Hello_World",
            "DATA_processing",
            "text123mining",
            "Clean_Data",
            "ANALYSIS_tools",
            "machine_learning",
            "Python_CODE",
            "statistics101",
            "Big_Data",
            "AI_systems",
            "deep_learning",
            "Neural_Networks",
            "Computer_Vision",
            "NLP_tasks",
            "Data_Science",
            "Feature_engineering",
            "Model_training",
            "Cross_validation",
            "Hyperparameter",
            "Optimization",
        ],
        "numbers": [
            "10,20,30",
            "5,15,25,35",
            "100",
            "1,2,3,4,5",
            "50,75",
            "200,300",
            "7,14,21",
            "80,90,100,110",
            "45",
            "33,66,99",
            "12,24,36,48",
            "5,10,15,20,25",
            "88,77,66",
            "150,250,350",
            "60",
            "11,22,33,44,55",
            "95,85,75",
            "40,50,60,70",
            "125",
            "8,16,24,32",
        ],
        "category": [
            "tech",
            "data",
            "text",
            "clean",
            "analysis",
            "ml",
            "code",
            "stats",
            "big",
            "ai",
            "dl",
            "neural",
            "vision",
            "nlp",
            "science",
            "feature",
            "model",
            "validation",
            "param",
            "opt",
        ],
        "value": np.random.uniform(50, 1500, 20).round(2),
        "timestamp": pd.date_range("2023-01-01", periods=20, freq="D"),
    }

    df = pd.DataFrame(data)
    df.to_csv("examples/advanced_data.csv", index=False)
    print("Sample data created: advanced_data.csv")
    return df


def example_map_operations():
    """Demonstrate map operations with lambda functions."""
    print("=== MAP OPERATIONS EXAMPLE ===")

    create_sample_data()

    config = {
        "input": {"type": "csv", "source": "examples/advanced_data.csv"},
        "output": {
            "columns": {
                # Simple text cleaning
                "cleaned_text": {
                    "source": "text",
                    "operations": [
                        {
                            "type": "map",
                            "function": "lambda x: str(x).strip().lower().replace('_', ' ')",
                        }
                    ],
                },
                # Extract and process numbers
                "number_count": {
                    "source": "numbers",
                    "operations": [
                        {"type": "map", "function": "lambda x: len(str(x).split(','))"}
                    ],
                    "type": "int",
                },
                # Complex text analysis
                "text_stats": {
                    "source": "text",
                    "operations": [
                        {
                            "type": "map",
                            "function": "lambda x: f'Length: {len(x)}, Words: {len(x.split(\"_\"))}, HasDigits: {any(c.isdigit() for c in x)}'",
                        }
                    ],
                },
            }
        },
    }

    dt = DataTidy()
    dt.load_config(config)
    result = dt.process_data()

    print("Map operations result:")
    print(result[["cleaned_text", "number_count", "text_stats"]].head(10))
    print()


def example_filter_operations():
    """Demonstrate filter operations."""
    print("=== FILTER OPERATIONS EXAMPLE ===")

    config = {
        "input": {"type": "csv", "source": "examples/advanced_data.csv"},
        "output": {
            "columns": {
                # Filter high values
                "high_values_only": {
                    "source": "value",
                    "operations": [
                        {
                            "type": "filter",
                            "condition": "lambda x: x > 500",
                            "fill_value": 0,
                        }
                    ],
                    "type": "float",
                },
                # Filter valid categories
                "valid_categories": {
                    "source": "category",
                    "operations": [
                        {
                            "type": "filter",
                            "condition": "lambda x: len(str(x)) > 2",
                            "fill_value": "short",
                        }
                    ],
                },
                # Keep original for comparison
                "original_value": {"source": "value", "type": "float"},
            }
        },
    }

    dt = DataTidy()
    dt.load_config(config)
    result = dt.process_data()

    print("Filter operations result:")
    print(result[["original_value", "high_values_only", "valid_categories"]].head(10))
    print()


def example_reduce_operations():
    """Demonstrate reduce operations."""
    print("=== REDUCE OPERATIONS EXAMPLE ===")

    config = {
        "input": {"type": "csv", "source": "examples/advanced_data.csv"},
        "output": {
            "columns": {
                # Sum all values
                "total_sum": {
                    "source": "value",
                    "operations": [
                        {
                            "type": "reduce",
                            "function": "lambda acc, x: acc + x",
                            "initial_value": 0,
                        }
                    ],
                    "type": "float",
                },
                # Find maximum value
                "max_value": {
                    "source": "value",
                    "operations": [
                        {
                            "type": "reduce",
                            "function": "lambda acc, x: max(acc, x)",
                            "initial_value": 0,
                        }
                    ],
                    "type": "float",
                },
                # Concatenate all categories
                "all_categories": {
                    "source": "category",
                    "operations": [
                        {
                            "type": "reduce",
                            "function": "lambda acc, x: acc + ',' + str(x) if acc else str(x)",
                        }
                    ],
                },
            }
        },
    }

    dt = DataTidy()
    dt.load_config(config)
    result = dt.process_data()

    print("Reduce operations result:")
    print(result[["total_sum", "max_value", "all_categories"]].head(3))
    print()


def example_window_operations():
    """Demonstrate window operations."""
    print("=== WINDOW OPERATIONS EXAMPLE ===")

    config = {
        "input": {"type": "csv", "source": "examples/advanced_data.csv"},
        "output": {
            "columns": {
                # 3-day moving average
                "moving_avg_3": {
                    "source": "value",
                    "operations": [
                        {"type": "window", "window_size": 3, "function": "mean"}
                    ],
                    "type": "float",
                },
                # Rolling maximum
                "rolling_max_5": {
                    "source": "value",
                    "operations": [
                        {"type": "window", "window_size": 5, "function": "max"}
                    ],
                    "type": "float",
                },
                # Custom rolling calculation
                "rolling_range": {
                    "source": "value",
                    "operations": [
                        {
                            "type": "window",
                            "window_size": 4,
                            "function": "lambda x: x.max() - x.min()",
                        }
                    ],
                    "type": "float",
                },
                # Original value for comparison
                "original_value": {"source": "value", "type": "float"},
            }
        },
    }

    dt = DataTidy()
    dt.load_config(config)
    result = dt.process_data()

    print("Window operations result:")
    print(
        result[
            ["original_value", "moving_avg_3", "rolling_max_5", "rolling_range"]
        ].head(10)
    )
    print()


def example_chained_operations():
    """Demonstrate chaining multiple operations."""
    print("=== CHAINED OPERATIONS EXAMPLE ===")

    config = {
        "input": {"type": "csv", "source": "examples/advanced_data.csv"},
        "output": {
            "columns": {
                # Chain: clean -> filter -> format
                "processed_text": {
                    "source": "text",
                    "operations": [
                        {
                            "type": "map",
                            "function": "lambda x: str(x).lower().replace('_', ' ')",
                        },
                        {
                            "type": "filter",
                            "condition": "lambda x: len(x) > 5",
                            "fill_value": "short",
                        },
                        {
                            "type": "map",
                            "function": "lambda x: x.title() if x != 'short' else 'SHORT'",
                        },
                    ],
                },
                # Chain: parse numbers -> calculate -> format
                "number_summary": {
                    "source": "numbers",
                    "operations": [
                        {
                            "type": "map",
                            "function": "lambda x: [float(n) for n in str(x).split(',')]",
                        },
                        {
                            "type": "map",
                            "function": "lambda x: {'sum': sum(x), 'avg': np.mean(x), 'count': len(x)}",
                        },
                        {
                            "type": "map",
                            "function": "lambda x: f\"Sum: {x['sum']:.1f}, Avg: {x['avg']:.1f}, Count: {x['count']}\"",
                        },
                    ],
                },
            }
        },
    }

    dt = DataTidy()
    dt.load_config(config)
    result = dt.process_data()

    print("Chained operations result:")
    print(result[["processed_text", "number_summary"]].head(10))
    print()


if __name__ == "__main__":
    print("=== ADVANCED COLUMN OPERATIONS WITH LAMBDA FUNCTIONS ===\n")

    example_map_operations()
    example_filter_operations()
    example_reduce_operations()
    example_window_operations()
    example_chained_operations()

    print("=== SUMMARY ===")
    print("DataTidy now supports advanced column operations:")
    print("✓ MAP: Apply lambda functions to each element")
    print("✓ FILTER: Keep elements matching conditions")
    print("✓ REDUCE: Aggregate column values with custom logic")
    print("✓ WINDOW: Rolling calculations with custom functions")
    print("✓ CHAINING: Combine multiple operations in sequence")
    print("✓ SECURITY: Safe execution environment with controlled functions")
    print("\nAll operations support lambda functions and complex data transformations!")
