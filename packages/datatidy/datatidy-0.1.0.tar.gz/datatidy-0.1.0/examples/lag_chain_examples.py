"""Examples demonstrating lag + chained operations combinations."""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from datatidy import DataTidy


def create_sample_trading_data():
    """Create sample trading data for lag+chain examples."""
    np.random.seed(456)

    # Generate 60 days of realistic trading data
    start_date = datetime(2023, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(60)]

    data = []
    base_price = 100.0

    for i in range(60):
        # Create realistic price movement with trends and reversals
        if i < 20:  # Uptrend phase
            trend = 0.15 * i
            volatility = 1.0
        elif i < 40:  # Consolidation phase
            trend = 3.0 + np.sin(i / 5) * 2
            volatility = 0.5
        else:  # Downtrend phase
            trend = 3.0 - 0.1 * (i - 40)
            volatility = 1.5

        daily_noise = np.random.normal(0, volatility)
        price = max(10, base_price + trend + daily_noise)

        # Volume inversely related to price stability
        price_change = (
            abs(price - base_price - trend) / base_price if base_price > 0 else 0
        )
        base_volume = 50000
        volume = base_volume * (1 + price_change * 3) + np.random.normal(0, 10000)

        data.append(
            {
                "date": dates[i].strftime("%Y-%m-%d"),
                "price": round(price, 2),
                "volume": int(max(10000, volume)),
                "symbol": "DEMO",
            }
        )

        base_price = price * 0.8 + base_price * 0.2  # Smooth base transition

    df = pd.DataFrame(data)
    df.to_csv("examples/time_series_data.csv", index=False)
    print("Sample trading data created: time_series_data.csv")
    return df


def example_basic_lag_chains():
    """Demonstrate basic lag + chain combinations."""
    print("=== BASIC LAG + CHAIN COMBINATIONS ===")

    create_sample_trading_data()

    # Simple configuration for basic patterns
    config = {
        "input": {"type": "csv", "source": "examples/time_series_data.csv"},
        "output": {
            "columns": {
                # Basic lag values
                "price_lag1": {
                    "transformation": "df['price'].shift(1)",
                    "type": "float",
                    "interim": True,
                },
                # Lag → Map chain: Price momentum
                "momentum_simple": {
                    "operations": [
                        {
                            "type": "map",
                            "function": "lambda x: (price - price_lag1) / price_lag1 if pd.notna(price_lag1) and price_lag1 > 0 else 0",
                        },
                        {
                            "type": "map",
                            "function": "lambda x: 'UP' if x > 0.02 else ('DOWN' if x < -0.02 else 'FLAT')",
                        },
                    ],
                    "source": "price",
                    "type": "string",
                },
                # Lag → Window → Map chain: Smoothed momentum
                "momentum_smooth": {
                    "operations": [
                        {
                            "type": "map",
                            "function": "lambda x: (price - price_lag1) / price_lag1 if pd.notna(price_lag1) and price_lag1 > 0 else 0",
                        },
                        {"type": "window", "window_size": 3, "function": "mean"},
                        {
                            "type": "map",
                            "function": "lambda x: 'STRONG_UP' if x > 0.03 else ('STRONG_DOWN' if x < -0.03 else 'NEUTRAL')",
                        },
                    ],
                    "source": "price",
                    "type": "string",
                },
            },
            "sort": [{"column": "date", "ascending": True}],
        },
        "global_settings": {"show_execution_plan": True},
    }

    dt = DataTidy()
    dt.load_config(config)
    result = dt.process_data()

    print("Basic lag+chain results:")
    print(result[["date", "price", "momentum_simple", "momentum_smooth"]].head(10))
    print()


def example_advanced_lag_chains():
    """Demonstrate advanced lag + chain combinations."""
    print("=== ADVANCED LAG + CHAIN COMBINATIONS ===")

    dt = DataTidy("examples/lag_chain_combinations.yaml")
    result = dt.process_data()

    print("Advanced lag+chain analysis:")
    columns_to_show = [
        "date",
        "price",
        "price_momentum_signal",
        "trend_strength_score",
        "volatility_regime",
        "multi_timeframe_signal",
        "master_signal",
    ]
    print(result[columns_to_show].head(15))
    print()

    print("Signal Distribution:")
    print("Price Momentum:", result["price_momentum_signal"].value_counts().to_dict())
    print("Volatility Regime:", result["volatility_regime"].value_counts().to_dict())
    print("Master Signal:", result["master_signal"].value_counts().to_dict())
    print()


def example_custom_lag_chain_patterns():
    """Demonstrate custom lag+chain pattern creation."""
    print("=== CUSTOM LAG + CHAIN PATTERNS ===")

    config = {
        "input": {"type": "csv", "source": "examples/time_series_data.csv"},
        "output": {
            "columns": {
                # Multi-lag foundation
                "price_lag1": {
                    "transformation": "df['price'].shift(1)",
                    "type": "float",
                    "interim": True,
                },
                "price_lag3": {
                    "transformation": "df['price'].shift(3)",
                    "type": "float",
                    "interim": True,
                },
                "price_lag5": {
                    "transformation": "df['price'].shift(5)",
                    "type": "float",
                    "interim": True,
                },
                # Pattern 1: Multi-lag → Filter → Reduce
                "acceleration_score": {
                    "operations": [
                        {
                            "type": "map",
                            "function": """
                            lambda x: [
                                (price - price_lag1) / price_lag1 if pd.notna(price_lag1) and price_lag1 > 0 else 0,
                                (price_lag1 - price_lag3) / price_lag3 if pd.notna(price_lag3) and price_lag3 > 0 else 0,
                                (price_lag3 - price_lag5) / price_lag5 if pd.notna(price_lag5) and price_lag5 > 0 else 0
                            ]
                            """,
                        },
                        {
                            "type": "filter",
                            "function": "lambda x: [val for val in x if pd.notna(val) and val != 0]",
                        },
                        {
                            "type": "reduce",
                            "function": "lambda acc, x: sum(x) / len(x) if len(x) > 0 else 0",
                            "initial_value": 0,
                        },
                    ],
                    "source": "price",
                    "type": "float",
                },
                # Pattern 2: Lag → Map → Window → Map
                "trend_consistency": {
                    "operations": [
                        {
                            "type": "map",
                            "function": "lambda x: 1 if price > price_lag1 else (-1 if price < price_lag1 else 0) if pd.notna(price_lag1) else 0",
                        },
                        {"type": "window", "window_size": 7, "function": "sum"},
                        {
                            "type": "map",
                            "function": "lambda x: abs(x) / 7.0",  # Consistency ratio
                        },
                        {
                            "type": "map",
                            "function": "lambda x: 'HIGH' if x > 0.7 else ('MEDIUM' if x > 0.4 else 'LOW')",
                        },
                    ],
                    "source": "price",
                    "type": "string",
                },
                # Pattern 3: Complex lag dependency with operations
                "regime_detection": {
                    "transformation": """
                    acc_score = acceleration_score if pd.notna(acceleration_score) else 0
                    consistency = trend_consistency if pd.notna(trend_consistency) else 'LOW'
                    
                    if acc_score > 0.02 and consistency == 'HIGH':
                        'TRENDING_UP'
                    elif acc_score < -0.02 and consistency == 'HIGH':
                        'TRENDING_DOWN'
                    elif consistency == 'LOW':
                        'CHOPPY'
                    else:
                        'TRANSITIONING'
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

    print("Custom lag+chain patterns:")
    print(
        result[
            [
                "date",
                "price",
                "acceleration_score",
                "trend_consistency",
                "regime_detection",
            ]
        ].head(12)
    )
    print()

    print("Regime Distribution:")
    print(result["regime_detection"].value_counts())
    print()


def example_lag_chain_performance_analysis():
    """Demonstrate performance analysis using lag+chain combinations."""
    print("=== LAG + CHAIN PERFORMANCE ANALYSIS ===")

    config = {
        "input": {"type": "csv", "source": "examples/time_series_data.csv"},
        "output": {
            "columns": {
                # Lag foundations
                "price_lag1": {
                    "transformation": "df['price'].shift(1)",
                    "type": "float",
                    "interim": True,
                },
                "price_lag5": {
                    "transformation": "df['price'].shift(5)",
                    "type": "float",
                    "interim": True,
                },
                "price_lag10": {
                    "transformation": "df['price'].shift(10)",
                    "type": "float",
                    "interim": True,
                },
                # Performance metrics using lag+chain
                "returns_1d": {
                    "operations": [
                        {
                            "type": "map",
                            "function": "lambda x: (price - price_lag1) / price_lag1 if pd.notna(price_lag1) and price_lag1 > 0 else 0",
                        },
                        {
                            "type": "map",
                            "function": "lambda x: x * 100",
                        },  # Convert to percentage
                    ],
                    "source": "price",
                    "type": "float",
                },
                "returns_5d": {
                    "operations": [
                        {
                            "type": "map",
                            "function": "lambda x: (price - price_lag5) / price_lag5 if pd.notna(price_lag5) and price_lag5 > 0 else 0",
                        },
                        {"type": "map", "function": "lambda x: x * 100"},
                    ],
                    "source": "price",
                    "type": "float",
                },
                # Rolling Sharpe ratio using lag+chain
                "rolling_sharpe": {
                    "operations": [
                        {
                            "type": "map",
                            "function": "lambda x: (price - price_lag1) / price_lag1 if pd.notna(price_lag1) and price_lag1 > 0 else 0",
                        },
                        {
                            "type": "window",
                            "window_size": 10,
                            "function": "lambda x: x.mean() / x.std() if x.std() > 0 else 0",
                        },
                    ],
                    "source": "price",
                    "type": "float",
                },
                # Max drawdown calculation
                "rolling_max": {
                    "operations": [
                        {"type": "window", "window_size": 20, "function": "max"}
                    ],
                    "source": "price",
                    "type": "float",
                    "interim": True,
                },
                "drawdown_pct": {
                    "transformation": "(rolling_max - price) / rolling_max * 100 if rolling_max > 0 else 0",
                    "type": "float",
                },
                # Performance classification
                "performance_category": {
                    "transformation": """
                    if returns_5d > 10:
                        'STRONG_WINNER'
                    elif returns_5d > 5:
                        'WINNER'
                    elif returns_5d < -10:
                        'STRONG_LOSER'
                    elif returns_5d < -5:
                        'LOSER'
                    else:
                        'STABLE'
                    """,
                    "type": "string",
                },
            },
            "sort": [{"column": "date", "ascending": True}],
        },
        "global_settings": {"show_execution_plan": True},
    }

    dt = DataTidy()
    dt.load_config(config)
    result = dt.process_data()

    print("Performance analysis with lag+chain:")
    perf_cols = [
        "date",
        "price",
        "returns_1d",
        "returns_5d",
        "rolling_sharpe",
        "drawdown_pct",
        "performance_category",
    ]
    print(result[perf_cols].head(15))
    print()

    print("Performance Summary:")
    print(f"Best 1D Return: {result['returns_1d'].max():.2f}%")
    print(f"Worst 1D Return: {result['returns_1d'].min():.2f}%")
    print(f"Max Drawdown: {result['drawdown_pct'].max():.2f}%")
    print(f"Average Sharpe: {result['rolling_sharpe'].mean():.2f}")
    print()

    print("Performance Categories:")
    print(result["performance_category"].value_counts())
    print()


def run_all_lag_chain_examples():
    """Run all lag+chain combination examples."""
    print("=== LAG + CHAINED OPERATIONS COMBINATIONS ===")
    print("Demonstrates powerful time series analysis patterns\\n")

    example_basic_lag_chains()
    example_advanced_lag_chains()
    example_custom_lag_chain_patterns()
    example_lag_chain_performance_analysis()

    print("=== LAG + CHAIN OPERATION PATTERNS ===")
    print("1. Lag → Map: Basic calculations using previous values")
    print("2. Lag → Map → Map: Multi-step transformations")
    print("3. Lag → Window → Map: Smoothed lag-based indicators")
    print("4. Multi-lag → Filter → Reduce: Complex trend analysis")
    print("5. Lag → Map → Window → Map: Rolling calculations with lags")
    print("6. Complex dependency chains with multiple lag+chain columns")
    print()

    print("=== KEY ADVANTAGES ===")
    print("✓ Combine historical data access with powerful transformations")
    print("✓ Create sophisticated technical indicators and signals")
    print("✓ Build multi-timeframe analysis systems")
    print("✓ Implement complex trading strategies and risk metrics")
    print("✓ Dependency resolution handles execution order automatically")
    print("✓ Interim columns enable complex calculation chains")
    print()

    print("=== AVAILABLE CONFIGURATIONS ===")
    print("📁 examples/lag_chain_combinations.yaml - Advanced patterns")
    print("📁 examples/lag_operations_example.yaml - Basic lag operations")
    print("📁 examples/advanced_lag_example.yaml - Trading signals")


if __name__ == "__main__":
    run_all_lag_chain_examples()
