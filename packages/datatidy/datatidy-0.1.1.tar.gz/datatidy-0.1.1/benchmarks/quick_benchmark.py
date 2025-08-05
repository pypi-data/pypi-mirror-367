#!/usr/bin/env python3
"""
Quick performance benchmark for DataTidy fallback system overhead.

This script provides a focused benchmark to measure the performance impact
of the enhanced fallback processing in realistic scenarios.
"""

import time
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import statistics

# Add the parent directory to the path to import datatidy
sys.path.insert(0, str(Path(__file__).parent.parent))

from datatidy import DataTidy
from datatidy.transformation.engine import TransformationEngine
from datatidy.fallback.processor import FallbackProcessor
from datatidy.fallback.logger import EnhancedLogger


def create_test_data(rows=10000):
    """Create realistic test data."""
    np.random.seed(42)

    return pd.DataFrame(
        {
            "id": range(1, rows + 1),
            "name": [
                f"Record_{i}" if i % 100 != 0 else None for i in range(1, rows + 1)
            ],
            "amount": np.random.lognormal(8, 1, rows),
            "score": np.random.normal(75, 15, rows),
            "category": np.random.choice(["A", "B", "C"], rows),
            "ratio": np.random.uniform(0.5, 2.0, rows),
        }
    )


def create_simple_config():
    """Create a simple configuration for testing."""
    return {
        "output": {
            "columns": {
                "id": {"source": "id", "type": "int"},
                "clean_name": {
                    "source": "name",
                    "type": "string",
                    "default": "Unknown",
                },
                "amount_category": {
                    "transformation": "'high' if amount > 5000 else 'low'",
                    "type": "string",
                },
                "normalized_score": {
                    "transformation": "(score - 50) / 25",
                    "type": "float",
                },
            }
        },
        "global_settings": {"processing_mode": "strict"},
    }


def create_partial_config():
    """Create a partial processing configuration."""
    config = create_simple_config()
    config["global_settings"] = {
        "processing_mode": "partial",
        "enable_partial_processing": True,
        "enable_fallback": True,
    }
    return config


def benchmark_processing(data, config, runs=5):
    """Benchmark processing with multiple runs."""
    times = []

    for _ in range(runs):
        dt = DataTidy()
        dt.config = config
        dt.transformation_engine = TransformationEngine(config)

        start_time = time.perf_counter()
        try:
            result_df = dt.transformation_engine.transform(data)
            success = True
        except Exception:
            success = False
        end_time = time.perf_counter()

        times.append(end_time - start_time)

    return {
        "avg_time": statistics.mean(times),
        "min_time": min(times),
        "max_time": max(times),
        "success": success,
    }


def benchmark_fallback_processing(data, config, runs=5):
    """Benchmark fallback processing with multiple runs."""
    times = []
    results = []

    for _ in range(runs):
        dt = DataTidy()
        dt.config = config
        dt.transformation_engine = TransformationEngine(config)
        dt.logger = EnhancedLogger()
        dt.fallback_processor = FallbackProcessor(config, dt.logger)

        start_time = time.perf_counter()
        try:
            result = dt.fallback_processor.process_with_fallback(
                data, dt.transformation_engine
            )
            success = result.success
            fallback_used = result.fallback_used
        except Exception:
            success = False
            fallback_used = False
        end_time = time.perf_counter()

        times.append(end_time - start_time)
        results.append({"success": success, "fallback_used": fallback_used})

    return {
        "avg_time": statistics.mean(times),
        "min_time": min(times),
        "max_time": max(times),
        "success": all(r["success"] for r in results),
        "fallback_used": any(r["fallback_used"] for r in results),
    }


def main():
    """Run focused performance benchmark."""
    print("🚀 DataTidy Fallback System - Quick Performance Benchmark")
    print("=" * 65)

    # Test different data sizes
    sizes = [1000, 5000, 10000, 25000]

    print("\n📊 Performance Overhead Analysis")
    print("-" * 50)
    print(f"{'Size':<8} {'Original':<12} {'Fallback':<12} {'Overhead':<12}")
    print("-" * 50)

    all_overheads = []

    for size in sizes:
        print(f"{size:,} rows", end="", flush=True)

        # Create test data
        data = create_test_data(size)
        simple_config = create_simple_config()
        partial_config = create_partial_config()

        # Benchmark original processing
        original_result = benchmark_processing(data, simple_config, runs=3)

        # Benchmark fallback processing
        fallback_result = benchmark_fallback_processing(data, partial_config, runs=3)

        # Calculate overhead
        if original_result["avg_time"] > 0:
            overhead_ms = (
                fallback_result["avg_time"] - original_result["avg_time"]
            ) * 1000
            overhead_pct = (overhead_ms / (original_result["avg_time"] * 1000)) * 100
        else:
            overhead_ms = 0
            overhead_pct = 0

        all_overheads.append(overhead_pct)

        print(
            f"   {original_result['avg_time']*1000:8.1f}ms   "
            f"{fallback_result['avg_time']*1000:8.1f}ms   "
            f"{overhead_pct:+6.1f}%"
        )

    # Summary statistics
    print("-" * 50)
    print(f"\n📈 Summary Statistics:")
    print(f"   Average overhead: {statistics.mean(all_overheads):+.1f}%")
    print(f"   Minimum overhead: {min(all_overheads):+.1f}%")
    print(f"   Maximum overhead: {max(all_overheads):+.1f}%")

    if len(all_overheads) > 1:
        print(f"   Standard deviation: ±{statistics.stdev(all_overheads):.1f}%")

    # Test with problematic data
    print(f"\n🧪 Reliability Test (with data quality issues)")
    print("-" * 50)

    # Create problematic data
    problem_data = create_test_data(5000)
    problem_data.loc[::10, "score"] = -999  # Invalid scores
    problem_data.loc[::20, "amount"] = None  # Missing amounts

    # Complex config that will fail on strict mode
    complex_config = {
        "output": {
            "columns": {
                "id": {"source": "id", "type": "int", "validation": {"required": True}},
                "validated_score": {
                    "source": "score",
                    "type": "float",
                    "validation": {"min_value": 0, "max_value": 100},
                },
                "calculated_amount": {
                    "transformation": "amount * 1.1",
                    "type": "float",
                    "validation": {"required": True},
                },
            }
        },
        "global_settings": {"processing_mode": "strict"},
    }

    # Test strict mode (will likely fail)
    print("Strict mode processing...", end="", flush=True)
    strict_result = benchmark_processing(problem_data, complex_config, runs=1)
    print(f" {'✅ Success' if strict_result['success'] else '❌ Failed'}")

    # Test partial mode (should handle gracefully)
    partial_complex_config = complex_config.copy()
    partial_complex_config["global_settings"] = {
        "processing_mode": "partial",
        "enable_partial_processing": True,
    }

    print("Partial mode processing...", end="", flush=True)
    partial_result = benchmark_fallback_processing(
        problem_data, partial_complex_config, runs=1
    )
    print(f" {'✅ Success' if partial_result['success'] else '❌ Failed'}")

    # Calculate reliability improvement
    print(f"\n💡 Key Insights:")

    avg_overhead = statistics.mean(all_overheads)
    if avg_overhead < 15:
        assessment = "✅ Low overhead"
    elif avg_overhead < 30:
        assessment = "⚠️  Moderate overhead"
    else:
        assessment = "🚨 High overhead"

    print(f"   Performance: {assessment} ({avg_overhead:+.1f}% average)")

    if partial_result["success"] and not strict_result["success"]:
        print(f"   Reliability: ✅ Fallback system prevents failures")
    else:
        print(f"   Reliability: ℹ️  Both modes performed similarly")

    print(f"\n🎯 Conclusion:")
    print(f"   The fallback system adds {avg_overhead:+.1f}% overhead on average")
    print(f"   while providing enhanced reliability and error handling.")

    if avg_overhead < 20:
        print(f"   This is excellent for production use! 🚀")
    elif avg_overhead < 40:
        print(f"   This is acceptable for most production scenarios. ✅")
    else:
        print(f"   Consider optimization for performance-critical applications. ⚠️")


if __name__ == "__main__":
    main()
