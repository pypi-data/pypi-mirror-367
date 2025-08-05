"""Tests for expression parser."""

import unittest
import pandas as pd
import numpy as np
from datatidy.transformation.expressions import ExpressionParser, SafeExpressionParser


class TestSafeExpressionParser(unittest.TestCase):
    """Test cases for SafeExpressionParser."""

    def setUp(self):
        """Set up test fixtures."""
        self.parser = SafeExpressionParser()
        self.context = {"x": 10, "y": 5, "name": "John Doe", "age": 25, "active": True}

    def test_arithmetic_operations(self):
        """Test arithmetic operations."""
        self.assertEqual(self.parser.parse("x + y", self.context), 15)
        self.assertEqual(self.parser.parse("x - y", self.context), 5)
        self.assertEqual(self.parser.parse("x * y", self.context), 50)
        self.assertEqual(self.parser.parse("x / y", self.context), 2.0)
        self.assertEqual(self.parser.parse("x // y", self.context), 2)
        self.assertEqual(self.parser.parse("x % y", self.context), 0)
        self.assertEqual(self.parser.parse("x ** 2", self.context), 100)

    def test_comparison_operations(self):
        """Test comparison operations."""
        self.assertTrue(self.parser.parse("x > y", self.context))
        self.assertFalse(self.parser.parse("x < y", self.context))
        self.assertTrue(self.parser.parse("x >= 10", self.context))
        self.assertTrue(self.parser.parse("x == 10", self.context))
        self.assertTrue(self.parser.parse("x != y", self.context))

    def test_logical_operations(self):
        """Test logical operations."""
        context = {"a": True, "b": False}
        self.assertTrue(self.parser.parse("a and True", context))
        self.assertTrue(self.parser.parse("a or b", context))
        self.assertFalse(self.parser.parse("not a", context))

    def test_string_operations(self):
        """Test string operations."""
        self.assertEqual(self.parser.parse("name.upper()", self.context), "JOHN DOE")
        self.assertEqual(self.parser.parse("name.lower()", self.context), "john doe")
        self.assertEqual(self.parser.parse("name.title()", self.context), "John Doe")
        self.assertTrue(self.parser.parse("name.startswith('John')", self.context))
        self.assertEqual(self.parser.parse("len(name)", self.context), 8)

    def test_conditional_expressions(self):
        """Test conditional (ternary) expressions."""
        result = self.parser.parse("'adult' if age >= 18 else 'minor'", self.context)
        self.assertEqual(result, "adult")

        context_minor = {"age": 16}
        result = self.parser.parse("'adult' if age >= 18 else 'minor'", context_minor)
        self.assertEqual(result, "minor")

    def test_list_operations(self):
        """Test list operations."""
        context = {"items": [1, 2, 3, 4, 5]}
        self.assertEqual(self.parser.parse("len(items)", context), 5)
        self.assertEqual(self.parser.parse("max(items)", context), 5)
        self.assertEqual(self.parser.parse("min(items)", context), 1)
        self.assertTrue(self.parser.parse("3 in items", context))
        self.assertFalse(self.parser.parse("6 in items", context))

    def test_safe_functions(self):
        """Test safe built-in functions."""
        self.assertEqual(self.parser.parse("abs(-5)", {}), 5)
        self.assertEqual(self.parser.parse("round(3.14159, 2)", {}), 3.14)
        self.assertEqual(self.parser.parse("str(123)", {}), "123")
        self.assertEqual(self.parser.parse("int('456')", {}), 456)
        self.assertEqual(self.parser.parse("float('7.89')", {}), 7.89)

    def test_unsafe_operations_blocked(self):
        """Test that unsafe operations are blocked."""
        # These should raise ValueError due to unsafe operations
        unsafe_expressions = [
            "__import__('os')",
            "exec('print(1)')",
            "eval('1+1')",
            "open('file.txt')",
        ]

        for expr in unsafe_expressions:
            with self.assertRaises(ValueError):
                self.parser.parse(expr, {})

    def test_error_handling(self):
        """Test error handling for invalid expressions."""
        with self.assertRaises(ValueError):
            self.parser.parse("invalid syntax [", {})

        with self.assertRaises(ValueError):
            self.parser.parse("undefined_variable", {})


class TestExpressionParser(unittest.TestCase):
    """Test cases for ExpressionParser."""

    def setUp(self):
        """Set up test fixtures."""
        self.parser = ExpressionParser()
        self.sample_data = pd.DataFrame(
            {
                "name": ["John Doe", "Jane Smith", "Bob Johnson"],
                "age": [25, 30, 35],
                "salary": [50000, 75000, 100000],
                "active": [True, False, True],
            }
        )

    def test_evaluate_simple_column(self):
        """Test evaluating simple column reference."""
        row = self.sample_data.iloc[0]
        result = self.parser.evaluate("name", row)
        self.assertEqual(result, "John Doe")

    def test_evaluate_transformation(self):
        """Test evaluating transformation expression."""
        row = self.sample_data.iloc[0]
        result = self.parser.evaluate("name.upper()", row)
        self.assertEqual(result, "JOHN DOE")

    def test_evaluate_conditional(self):
        """Test evaluating conditional expression."""
        row = self.sample_data.iloc[0]
        result = self.parser.evaluate("'high' if salary > 60000 else 'low'", row)
        self.assertEqual(result, "low")

        row = self.sample_data.iloc[2]
        result = self.parser.evaluate("'high' if salary > 60000 else 'low'", row)
        self.assertEqual(result, "high")

    def test_evaluate_vectorized_simple(self):
        """Test vectorized evaluation of simple expressions."""
        result = self.parser.evaluate_vectorized("name", self.sample_data)
        self.assertIsInstance(result, pd.Series)
        self.assertEqual(len(result), 3)
        self.assertEqual(result.iloc[0], "John Doe")

    def test_evaluate_vectorized_complex(self):
        """Test vectorized evaluation of complex expressions."""
        result = self.parser.evaluate_vectorized(
            "'senior' if age > 30 else 'junior'", self.sample_data
        )
        self.assertIsInstance(result, pd.Series)
        self.assertEqual(len(result), 3)
        self.assertEqual(result.iloc[0], "junior")  # age 25
        self.assertEqual(result.iloc[1], "junior")  # age 30
        self.assertEqual(result.iloc[2], "senior")  # age 35

    def test_evaluate_with_numpy(self):
        """Test evaluation with numpy functions."""
        df = pd.DataFrame(
            {
                "values": [1.1, 2.7, 3.9, 4.2],
            }
        )

        # Test with numpy functions available in context
        result = self.parser.evaluate_vectorized("values.round()", df)
        expected = pd.Series([1.0, 3.0, 4.0, 4.0])
        pd.testing.assert_series_equal(result, expected)

    def test_error_handling_vectorized(self):
        """Test error handling in vectorized evaluation."""
        # Should fall back to row-by-row evaluation for complex cases
        result = self.parser.evaluate_vectorized(
            "name.split()[0]", self.sample_data  # This might require fallback
        )
        self.assertIsInstance(result, pd.Series)
        self.assertEqual(result.iloc[0], "John")


if __name__ == "__main__":
    unittest.main()
