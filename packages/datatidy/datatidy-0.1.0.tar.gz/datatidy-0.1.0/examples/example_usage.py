#!/usr/bin/env python3
"""
Example usage of DataTidy package.

This script demonstrates various ways to use DataTidy for data processing.
"""

import pandas as pd
from datatidy import DataTidy


def example_basic_usage():
    """Basic usage example with dictionary configuration."""
    print("=== Basic Usage Example ===")

    # Sample data
    data = pd.DataFrame(
        {
            "id": [1, 2, 3, 4],
            "name": [" John Doe ", "jane smith", "BOB WILSON", "Alice Brown "],
            "age": [25, 17, 45, 30],
            "salary": [50000, 25000, 95000, 72000],
        }
    )

    # Configuration
    config = {
        "input": {"type": "csv", "source": "not_used_when_passing_dataframe"},
        "output": {
            "columns": {
                "user_id": {"source": "id", "type": "int"},
                "full_name": {
                    "source": "name",
                    "transformation": "str.strip().title()",
                    "type": "string",
                },
                "age_category": {
                    "transformation": "'adult' if age >= 18 else 'minor'",
                    "type": "string",
                },
                "salary_grade": {
                    "transformation": "'high' if salary > 80000 else ('medium' if salary > 60000 else 'low')",
                    "type": "string",
                },
            }
        },
    }

    # Process data
    dt = DataTidy(config)
    result = dt.process_data(data)

    print("Original data:")
    print(data)
    print("\nProcessed data:")
    print(result)
    print()


def example_file_processing():
    """Example processing CSV file with validation."""
    print("=== File Processing Example ===")

    # Use the sample configuration file
    dt = DataTidy("examples/sample_config.yaml")

    try:
        # Process the sample data file
        result = dt.process_data("examples/sample_data.csv")
        print("Successfully processed data:")
        print(result.head())

        # Check for any validation errors
        if dt.has_errors():
            print("\nValidation errors found:")
            for error in dt.get_errors():
                print(f"  - {error['message']}")
        else:
            print("\nNo validation errors!")

    except Exception as e:
        print(f"Error processing file: {e}")

    print()


def example_complex_transformations():
    """Example with complex transformations and validations."""
    print("=== Complex Transformations Example ===")

    # Sample e-commerce data
    data = pd.DataFrame(
        {
            "order_id": ["ORD001", "ORD002", "ORD003", "ORD004"],
            "customer_email": [
                "john@email.com",
                "invalid-email",
                "alice@test.com",
                "bob@company.co.uk",
            ],
            "order_date": ["2024-01-15", "2024-01-16", "2024-01-17", "2024-01-18"],
            "amount": [150.50, 75.25, 200.00, 45.99],
            "status": ["completed", "pending", "shipped", "cancelled"],
            "customer_age": [28, 34, 19, 52],
        }
    )

    config = {
        "input": {"type": "csv", "source": "not_used"},
        "output": {
            "columns": {
                "order_id": {
                    "source": "order_id",
                    "type": "string",
                    "validation": {"required": True, "pattern": r"^ORD\d{3}$"},
                },
                "email": {
                    "source": "customer_email",
                    "type": "string",
                    "validation": {
                        "required": True,
                        "pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
                    },
                },
                "order_month": {
                    "transformation": "pd.to_datetime(order_date).strftime('%B')",
                    "type": "string",
                },
                "amount_category": {
                    "transformation": "'large' if amount > 100 else ('medium' if amount > 50 else 'small')",
                    "type": "string",
                    "validation": {"allowed_values": ["small", "medium", "large"]},
                },
                "customer_segment": {
                    "transformation": "'senior' if customer_age >= 50 else ('adult' if customer_age >= 25 else 'young')",
                    "type": "string",
                },
                "is_active_order": {
                    "transformation": "status in ['pending', 'shipped']",
                    "type": "bool",
                },
            },
            "filters": [{"condition": "amount > 0", "action": "keep"}],
            "sort": [{"column": "amount_category", "ascending": False}],
        },
        "global_settings": {"ignore_errors": True, "max_errors": 5},
    }

    dt = DataTidy(config)
    result = dt.process_data(data)

    print("Original data:")
    print(data)
    print("\nProcessed data:")
    print(result)

    if dt.has_errors():
        print("\nValidation errors:")
        for error in dt.get_errors():
            print(f"  - {error['message']}")

    print()


def example_save_to_different_formats():
    """Example saving to different output formats."""
    print("=== Save to Different Formats Example ===")

    # Simple data
    data = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "name": ["Alice", "Bob", "Charlie"],
            "score": [85.5, 92.0, 78.5],
        }
    )

    config = {
        "input": {"type": "csv", "source": "not_used"},
        "output": {
            "columns": {
                "student_id": {"source": "id", "type": "int"},
                "student_name": {"source": "name", "type": "string"},
                "grade": {
                    "transformation": "'A' if score >= 90 else ('B' if score >= 80 else 'C')",
                    "type": "string",
                },
            }
        },
    }

    dt = DataTidy(config)

    # Save to different formats
    import tempfile
    import os

    with tempfile.TemporaryDirectory() as temp_dir:
        # Save as CSV
        csv_path = os.path.join(temp_dir, "output.csv")
        dt.process_and_save(csv_path, data)
        print(f"Saved to CSV: {csv_path}")

        # Save as Excel
        excel_path = os.path.join(temp_dir, "output.xlsx")
        dt.process_and_save(excel_path, data)
        print(f"Saved to Excel: {excel_path}")

        # Save as JSON
        json_path = os.path.join(temp_dir, "output.json")
        dt.process_and_save(json_path, data)
        print(f"Saved to JSON: {json_path}")

        # Read back and display CSV results
        result_df = pd.read_csv(csv_path)
        print("\nSaved data:")
        print(result_df)

    print()


def example_error_handling():
    """Example of error handling and debugging."""
    print("=== Error Handling Example ===")

    # Data with intentional issues
    problematic_data = pd.DataFrame(
        {
            "id": [1, -1, 3, "invalid"],  # Negative and string IDs
            "email": ["good@email.com", "bad-email", "", "another@test.com"],
            "age": [25, 150, -5, 30],  # Invalid ages
            "score": [85, 95, 101, 75],  # Score over 100
        }
    )

    strict_config = {
        "input": {"type": "csv", "source": "not_used"},
        "output": {
            "columns": {
                "user_id": {
                    "source": "id",
                    "type": "int",
                    "validation": {"required": True, "min_value": 1},
                },
                "email": {
                    "source": "email",
                    "type": "string",
                    "validation": {
                        "required": True,
                        "pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
                    },
                },
                "age": {
                    "source": "age",
                    "type": "int",
                    "validation": {"min_value": 0, "max_value": 120},
                },
                "score": {
                    "source": "score",
                    "type": "int",
                    "validation": {"min_value": 0, "max_value": 100},
                },
            }
        },
        "global_settings": {
            "ignore_errors": True,  # Continue processing despite errors
            "max_errors": 20,
        },
    }

    dt = DataTidy(strict_config)

    try:
        result = dt.process_data(problematic_data)
        print("Processed data (with errors ignored):")
        print(result)

        print(f"\nFound {len(dt.get_errors())} validation errors:")
        for i, error in enumerate(dt.get_errors(), 1):
            print(f"{i}. {error['message']}")

    except Exception as e:
        print(f"Processing failed: {e}")

    print()


if __name__ == "__main__":
    """Run all examples."""
    print("DataTidy Usage Examples")
    print("=" * 50)

    example_basic_usage()
    example_file_processing()
    example_complex_transformations()
    example_save_to_different_formats()
    example_error_handling()

    print("All examples completed!")
