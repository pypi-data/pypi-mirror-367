"""Examples demonstrating lag operations for time series analysis."""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from datatidy import DataTidy


def create_sample_time_series_data():
    """Create sample time series data for lag operation examples."""
    np.random.seed(42)

    # Generate 50 days of stock data
    start_date = datetime(2023, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(50)]

    # Simulate stock price with trend and noise
    base_price = 100
    prices = []
    volumes = []

    for i in range(50):
        # Add trend and random walk
        trend = 0.1 * i  # Slight upward trend
        noise = np.random.normal(0, 2)  # Daily volatility
        price = (
            base_price + trend + noise + (5 * np.sin(i / 10))
        )  # Add cyclical pattern
        prices.append(max(10, price))  # Ensure positive prices

        # Volume inversely correlated with price changes
        base_volume = 10000
        volume_noise = np.random.normal(0, 2000)
        volume = base_volume + volume_noise + (1000 * abs(noise))
        volumes.append(max(1000, volume))

    # Create DataFrame
    data = {"date": dates, "price": prices, "volume": volumes, "symbol": ["AAPL"] * 50}

    df = pd.DataFrame(data)
    df.to_csv("examples/time_series_data.csv", index=False)
    print("Sample time series data created: time_series_data.csv")
    return df


def create_sample_stock_data():
    """Create comprehensive stock data for advanced lag examples."""
    np.random.seed(123)

    # Generate 100 days of OHLCV data
    start_date = datetime(2023, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(100)]

    data = []
    base_price = 150.0

    for i in range(100):
        # Generate realistic OHLCV data
        trend = 0.05 * i  # Slight upward trend
        daily_noise = np.random.normal(0, 1.5)

        # Previous close (for gap calculation)
        prev_close = base_price + trend + (daily_noise if i > 0 else 0)

        # Today's open (can gap up/down)
        gap = np.random.normal(0, 0.5)
        open_price = prev_close + gap

        # Intraday range
        daily_range = abs(np.random.normal(0, 2))
        high_price = open_price + daily_range * np.random.uniform(0.5, 1)
        low_price = open_price - daily_range * np.random.uniform(0.3, 0.8)

        # Close within the range
        close_price = low_price + (high_price - low_price) * np.random.uniform(0.2, 0.8)

        # Volume (higher on big moves)
        price_change = abs(close_price - open_price) / open_price
        base_volume = 50000
        volume = base_volume * (1 + price_change * 5) + np.random.normal(0, 10000)

        data.append(
            {
                "date": dates[i].strftime("%Y-%m-%d"),
                "open": round(max(10, open_price), 2),
                "high": round(max(10, high_price), 2),
                "low": round(max(10, low_price), 2),
                "close": round(max(10, close_price), 2),
                "volume": int(max(1000, volume)),
                "symbol": "MSFT",
            }
        )

        base_price = close_price  # Update base for next day

    df = pd.DataFrame(data)
    df.to_csv("examples/stock_data.csv", index=False)
    print("Sample stock data created: stock_data.csv")
    return df


def example_basic_lag_operations():
    """Demonstrate basic lag operations."""
    print("=== BASIC LAG OPERATIONS ===")
    print("Using configuration: lag_operations_example.yaml")

    create_sample_time_series_data()

    dt = DataTidy("examples/lag_operations_example.yaml")
    result = dt.process_data()

    print("Lag operations result (showing price changes based on previous values):")
    columns_to_show = [
        "date",
        "price",
        "price_change",
        "price_change_pct",
        "volume_momentum",
        "ma_signal",
    ]
    print(result[columns_to_show].head(10))
    print()
    print("Key insights:")
    print("- First row has NaN for lag-based calculations (no previous data)")
    print("- price_change = current_price - previous_price")
    print("- price_change_pct shows percentage change from previous day")
    print("- ma_signal compares current price to lagged moving average")
    print()


def example_advanced_lag_analysis():
    """Demonstrate advanced lag-based analysis."""
    print("=== ADVANCED LAG ANALYSIS ===")
    print("Using configuration: advanced_lag_example.yaml")

    create_sample_stock_data()

    dt = DataTidy("examples/advanced_lag_example.yaml")
    result = dt.process_data()

    print("Advanced lag analysis (stock trading signals):")
    columns_to_show = [
        "date",
        "close",
        "daily_return",
        "gap_percent",
        "volume_price_divergence",
        "trading_recommendation",
    ]
    print(result[columns_to_show].head(15))
    print()

    # Show summary statistics
    print("Trading Signal Distribution:")
    print(result["trading_recommendation"].value_counts())
    print()

    print("Breakout Analysis:")
    print(result["breakout_strength"].value_counts())
    print()


def example_custom_lag_formula():
    """Demonstrate custom lag formula creation."""
    print("=== CUSTOM LAG FORMULAS ===")

    # Create a custom configuration for specific lag patterns
    config = {
        "input": {"type": "csv", "source": "examples/time_series_data.csv"},
        "output": {
            "columns": {
                # Custom lag formula: current value based on 3-period lag
                "price_vs_3day_lag": {
                    "transformation": "price / df['price'].shift(3) if pd.notna(df['price'].shift(3)) and df['price'].shift(3) > 0 else 1",
                    "type": "float",
                },
                # Rolling correlation with lag
                "price_volume_lag_corr": {
                    "operations": [
                        {
                            "type": "window",
                            "window_size": 10,
                            "function": "lambda x: x.corr(df['volume'].shift(1).rolling(10).mean()) if len(x) >= 5 else 0",
                        }
                    ],
                    "source": "price",
                    "type": "float",
                },
                # Complex multi-lag pattern
                "momentum_pattern": {
                    "transformation": """
                    p1 = df['price'].shift(1)
                    p2 = df['price'].shift(2)
                    p3 = df['price'].shift(3)
                    
                    if all(pd.notna([p1, p2, p3])):
                        # Accelerating momentum
                        if price > p1 > p2 > p3:
                            'ACCELERATING_UP'
                        elif price < p1 < p2 < p3:
                            'ACCELERATING_DOWN'
                        # Decelerating momentum
                        elif price > p1 and p1 < p2:
                            'DECELERATING_UP'
                        elif price < p1 and p1 > p2:
                            'DECELERATING_DOWN'
                        else:
                            'SIDEWAYS'
                    else:
                        'INSUFFICIENT_DATA'
                    """,
                    "type": "string",
                },
                # Lag-based volatility
                "realized_volatility": {
                    "operations": [
                        {
                            "type": "map",
                            "function": """
                            lambda x: (
                                df['price'].pct_change().rolling(5).std().iloc[x.name] * 100
                                if x.name >= 4 else 0
                            )
                            """,
                        }
                    ],
                    "source": "price",
                    "type": "float",
                },
            },
            "sort": [{"column": "date", "ascending": True}],
        },
        "global_settings": {"show_execution_plan": True},
    }

    dt = DataTidy()
    dt.load_config(config)
    result = dt.process_data()

    print("Custom lag formulas result:")
    columns_to_show = [
        "date",
        "price",
        "price_vs_3day_lag",
        "momentum_pattern",
        "realized_volatility",
    ]
    print(result[columns_to_show].head(10))
    print()


def example_lag_dependency_chains():
    """Demonstrate lag operations in dependency chains."""
    print("=== LAG OPERATIONS IN DEPENDENCY CHAINS ===")

    config = {
        "input": {"type": "csv", "source": "examples/time_series_data.csv"},
        "output": {
            "columns": {
                # Step 1: Basic lags
                "price_lag1": {
                    "transformation": "df['price'].shift(1)",
                    "type": "float",
                    "interim": True,
                },
                "price_lag2": {
                    "transformation": "df['price'].shift(2)",
                    "type": "float",
                    "interim": True,
                },
                # Step 2: Calculations using lags
                "short_change": {
                    "transformation": "price - price_lag1 if pd.notna(price_lag1) else 0",
                    "type": "float",
                    "interim": True,
                },
                "medium_change": {
                    "transformation": "price - price_lag2 if pd.notna(price_lag2) else 0",
                    "type": "float",
                    "interim": True,
                },
                # Step 3: Signal based on lag calculations
                "acceleration_signal": {
                    "transformation": """
                    if pd.notna(short_change) and pd.notna(medium_change):
                        if short_change > 0 and medium_change > 0 and short_change > medium_change:
                            'ACCELERATING_UP'
                        elif short_change < 0 and medium_change < 0 and abs(short_change) > abs(medium_change):
                            'ACCELERATING_DOWN'
                        else:
                            'STABLE'
                    else:
                        'NO_SIGNAL'
                    """,
                    "type": "string",
                },
                # Step 4: Final recommendation using all previous calculations
                "final_signal": {
                    "transformation": """
                    f"Price: ${price:.2f}, 1D Change: {short_change:+.2f}, 2D Change: {medium_change:+.2f}, Signal: {acceleration_signal}"
                    """,
                    "type": "string",
                },
            },
            "sort": [{"column": "date", "ascending": True}],
        },
        "global_settings": {"show_execution_plan": True, "verbose": True},
    }

    dt = DataTidy()
    dt.load_config(config)
    result = dt.process_data()

    print("Lag dependency chain result:")
    print(result[["date", "price", "acceleration_signal", "final_signal"]].head(8))
    print()

    print("Signal Distribution:")
    print(result["acceleration_signal"].value_counts())
    print()


def run_all_lag_examples():
    """Run all lag operation examples."""
    print("=== LAG OPERATIONS FOR TIME SERIES ANALYSIS ===")
    print("Demonstrates calculations based on previous row values\n")

    example_basic_lag_operations()
    example_advanced_lag_analysis()
    example_custom_lag_formula()
    example_lag_dependency_chains()

    print("=== LAG OPERATION PATTERNS ===")
    print("1. df['column'].shift(n) - Basic lag by n periods")
    print("2. Rolling operations + shift - Lagged moving averages")
    print("3. Conditional logic with lag values - Signal generation")
    print("4. Multi-lag comparisons - Trend and momentum analysis")
    print("5. Lag dependency chains - Complex time series strategies")
    print()

    print("=== KEY CONCEPTS ===")
    print("✓ Always sort data by time before lag calculations")
    print("✓ First N rows will have NaN for N-period lags")
    print("✓ Use interim columns for lag values in complex calculations")
    print("✓ Dependency resolution works with lag-based formulas")
    print("✓ Combine multiple lag periods for sophisticated analysis")
    print()

    print("=== AVAILABLE YAML CONFIGURATIONS ===")
    print("📁 examples/lag_operations_example.yaml - Basic lag operations")
    print("📁 examples/advanced_lag_example.yaml - Advanced trading signals")


if __name__ == "__main__":
    run_all_lag_examples()
