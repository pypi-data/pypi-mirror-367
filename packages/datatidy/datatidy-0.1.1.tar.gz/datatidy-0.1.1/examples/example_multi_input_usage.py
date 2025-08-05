"""Example usage of DataTidy with multiple input sources."""

import pandas as pd
from datatidy import DataTidy


def create_sample_data():
    """Create sample data files for the multi-input example."""

    # Users data
    users_data = {
        "user_id": [1, 2, 3, 4, 5],
        "name": [
            "John Doe",
            "jane smith",
            "Bob Johnson",
            "Alice Brown",
            "Charlie Wilson",
        ],
        "email": [
            "john@example.com",
            "jane@test.com",
            "bob@demo.org",
            "alice@sample.net",
            "charlie@example.com",
        ],
        "signup_date": [
            "2023-01-15",
            "2023-02-20",
            "2023-03-10",
            "2023-01-25",
            "2023-02-28",
        ],
    }
    users_df = pd.DataFrame(users_data)
    users_df.to_csv("examples/users.csv", index=False)

    # Orders data (saved as parquet)
    orders_data = {
        "id": [101, 102, 103, 104, 105, 106],
        "user_id": [1, 2, 1, 3, 2, 4],
        "product_id": [201, 202, 203, 201, 204, 202],
        "total_amount": [299.99, 149.50, 89.99, 299.99, 199.00, 149.50],
        "created_at": [
            "2023-03-01",
            "2023-03-05",
            "2023-03-10",
            "2023-03-15",
            "2023-03-20",
            "2023-03-25",
        ],
    }
    orders_df = pd.DataFrame(orders_data)
    orders_df.to_parquet("examples/orders.parquet", index=False)

    # Products data (for database example - saved as CSV for demo)
    products_data = {
        "id": [201, 202, 203, 204, 205],
        "name": [
            "Laptop Pro",
            "Wireless Mouse",
            "USB Cable",
            "Monitor Stand",
            "Keyboard",
        ],
        "category": [
            "Electronics",
            "Electronics",
            "Electronics",
            "Accessories",
            "Electronics",
        ],
        "price": [299.99, 149.50, 89.99, 199.00, 79.99],
        "active": [True, True, True, True, False],
    }
    products_df = pd.DataFrame(products_data)
    products_df.to_csv("examples/products.csv", index=False)

    print("Sample data files created successfully!")


def example_multi_input_processing():
    """Demonstrate multi-input processing with joins."""

    # Create sample data
    create_sample_data()

    # Example 1: Multi-input with database simulation
    print("=== Example 1: Multi-Input with Simulated Database ===")

    # Modify the config to use CSV instead of database for demo
    config = {
        "inputs": {
            "users": {"type": "csv", "source": "examples/users.csv"},
            "orders": {"type": "parquet", "source": "examples/orders.parquet"},
            "products": {"type": "csv", "source": "examples/products.csv"},
        },
        "joins": [
            {
                "left": "users",
                "right": "orders",
                "on": "user_id",
                "how": "inner",
                "suffix": ["_user", "_order"],
            },
            {
                "left": "result",
                "right": "products",
                "on": {"left": "product_id", "right": "id"},
                "how": "left",
                "suffix": ["", "_product"],
            },
        ],
        "output": {
            "columns": {
                "customer_name": {
                    "source": "name_user",
                    "type": "string",
                    "transformation": "str.strip().title()",
                },
                "product_name": {
                    "source": "name_product",
                    "type": "string",
                    "default": "Unknown Product",
                },
                "order_total": {"source": "total_amount", "type": "float"},
                "order_summary": {
                    "transformation": "f'{customer_name} bought {product_name} for ${order_total:.2f}'",
                    "type": "string",
                },
            },
            "sort": [{"column": "customer_name", "ascending": True}],
        },
    }

    # Process the data
    dt = DataTidy()
    dt.load_config(config)
    result = dt.process_data()

    print("Multi-input join result:")
    print(result)
    print(f"Result shape: {result.shape}")
    print()


def example_simple_join():
    """Demonstrate simple two-table join."""

    print("=== Example 2: Simple Two-Table Join ===")

    # Create employee and department data
    employees_data = {
        "id": [1, 2, 3, 4],
        "name": ["john doe", "jane smith", "bob wilson", "alice brown"],
        "dept_id": [10, 20, 10, 30],
    }
    employees_df = pd.DataFrame(employees_data)
    employees_df.to_csv("examples/employees.csv", index=False)

    departments_data = {
        "dept_id": [10, 20, 30, 40],
        "name": ["Engineering", "Sales", "Marketing", "HR"],
    }
    departments_df = pd.DataFrame(departments_data)
    # Save as Excel for variety
    departments_df.to_excel("examples/departments.xlsx", index=False)

    # Configuration for simple join
    config = {
        "inputs": {
            "employees": {"type": "csv", "source": "examples/employees.csv"},
            "departments": {
                "type": "excel",
                "source": {"path": "examples/departments.xlsx", "sheet_name": "Sheet1"},
            },
        },
        "joins": [
            {
                "left": "employees",
                "right": "departments",
                "on": "dept_id",
                "how": "left",
                "suffix": ["", "_dept"],
            }
        ],
        "output": {
            "columns": {
                "employee_name": {
                    "source": "name",
                    "type": "string",
                    "transformation": "str.strip().title()",
                },
                "department": {
                    "source": "name_dept",
                    "type": "string",
                    "default": "Unknown",
                },
                "employee_info": {
                    "transformation": "f'{employee_name} works in {department}'"
                },
            }
        },
    }

    dt = DataTidy()
    dt.load_config(config)
    result = dt.process_data()

    print("Simple join result:")
    print(result)
    print()


def example_cross_join():
    """Demonstrate cross join functionality."""

    print("=== Example 3: Cross Join ===")

    # Create small datasets for cross join
    colors_data = {"color": ["Red", "Blue", "Green"]}
    sizes_data = {"size": ["Small", "Large"]}

    colors_df = pd.DataFrame(colors_data)
    sizes_df = pd.DataFrame(sizes_data)

    colors_df.to_csv("examples/colors.csv", index=False)
    sizes_df.to_csv("examples/sizes.csv", index=False)

    config = {
        "inputs": {
            "colors": {"type": "csv", "source": "examples/colors.csv"},
            "sizes": {"type": "csv", "source": "examples/sizes.csv"},
        },
        "joins": [
            {
                "left": "colors",
                "right": "sizes",
                "on": "dummy",  # Not used for cross join
                "how": "cross",
            }
        ],
        "output": {
            "columns": {
                "product_variant": {
                    "transformation": "f'{size} {color} Item'",
                    "type": "string",
                }
            }
        },
    }

    dt = DataTidy()
    dt.load_config(config)
    result = dt.process_data()

    print("Cross join result:")
    print(result)
    print()


if __name__ == "__main__":
    # Run examples
    example_multi_input_processing()
    example_simple_join()
    example_cross_join()

    print("=== Multi-Input Examples Complete ===")
    print("The new DataTidy multi-input system supports:")
    print("- Multiple input sources (CSV, Excel, Parquet, Pickle, Database)")
    print("- Various join types (inner, left, right, outer, cross)")
    print("- Complex transformations using data from multiple sources")
    print("- Flexible column referencing with automatic suffix handling")
