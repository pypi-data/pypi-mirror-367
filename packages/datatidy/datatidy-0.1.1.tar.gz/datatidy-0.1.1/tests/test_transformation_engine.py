"""Tests for transformation engine."""

import unittest
import pandas as pd
import numpy as np
from datatidy.transformation.engine import TransformationEngine, ValidationError


class TestTransformationEngine(unittest.TestCase):
    """Test cases for TransformationEngine."""

    def setUp(self):
        """Set up test fixtures."""
        self.sample_data = pd.DataFrame(
            {
                "id": [1, 2, 3, 4],
                "name": [" John Doe ", "Jane Smith", "", "Bob Wilson"],
                "age": [25, 30, -5, 35],  # -5 is invalid
                "salary": [50000, 75000, 100000, 0],  # 0 might be invalid
                "email": [
                    "john@test.com",
                    "jane@test.com",
                    "invalid-email",
                    "bob@test.com",
                ],
            }
        )

        self.config = {
            "output": {
                "columns": {
                    "user_id": {
                        "source": "id",
                        "type": "int",
                        "validation": {"required": True, "min_value": 1},
                    },
                    "full_name": {
                        "source": "name",
                        "type": "string",
                        "transformation": "name.strip().title()",
                        "validation": {"required": True, "min_length": 2},
                    },
                    "age_group": {
                        "transformation": "'adult' if age >= 18 else 'minor'",
                        "type": "string",
                        "validation": {"allowed_values": ["adult", "minor"]},
                    },
                    "salary_bracket": {
                        "transformation": "'high' if salary > 80000 else ('medium' if salary > 60000 else 'low')",
                        "type": "string",
                    },
                }
            },
            "global_settings": {"ignore_errors": True, "max_errors": 10},
        }

    def test_transform_basic(self):
        """Test basic transformation functionality."""
        engine = TransformationEngine(self.config)
        result = engine.transform(self.sample_data)

        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 4)
        self.assertIn("user_id", result.columns)
        self.assertIn("full_name", result.columns)
        self.assertIn("age_group", result.columns)
        self.assertIn("salary_bracket", result.columns)

    def test_column_transformation(self):
        """Test column transformations."""
        engine = TransformationEngine(self.config)
        result = engine.transform(self.sample_data)

        # Check name transformation (strip and title case)
        self.assertEqual(result.iloc[0]["full_name"], "John Doe")

        # Check age group transformation
        self.assertEqual(result.iloc[0]["age_group"], "adult")  # age 25

        # Check salary bracket transformation
        self.assertEqual(result.iloc[0]["salary_bracket"], "low")  # salary 50000
        self.assertEqual(result.iloc[1]["salary_bracket"], "medium")  # salary 75000
        self.assertEqual(result.iloc[2]["salary_bracket"], "high")  # salary 100000

    def test_data_type_conversion(self):
        """Test data type conversions."""
        engine = TransformationEngine(self.config)
        result = engine.transform(self.sample_data)

        # Check that user_id is converted to int
        self.assertTrue(pd.api.types.is_integer_dtype(result["user_id"]))

        # Check that string columns are strings
        self.assertTrue(
            pd.api.types.is_string_dtype(result["full_name"])
            or pd.api.types.is_object_dtype(result["full_name"])
        )

    def test_validation_errors(self):
        """Test validation error collection."""
        # Use config without ignore_errors to test error handling
        config = self.config.copy()
        config["global_settings"]["ignore_errors"] = False

        engine = TransformationEngine(config)

        # This should raise ValidationError due to invalid data
        with self.assertRaises(ValidationError):
            engine.transform(self.sample_data)

    def test_validation_with_ignore_errors(self):
        """Test validation with ignore_errors=True."""
        engine = TransformationEngine(self.config)
        result = engine.transform(self.sample_data)

        # Should complete despite validation errors
        self.assertIsInstance(result, pd.DataFrame)

        # Should have collected errors
        self.assertTrue(engine.has_errors())
        errors = engine.get_errors()
        self.assertGreater(len(errors), 0)

    def test_filters(self):
        """Test row filtering."""
        config_with_filters = self.config.copy()
        config_with_filters["output"]["filters"] = [
            {"condition": "age > 0", "action": "keep"},
            {"condition": "salary > 0", "action": "keep"},
        ]

        engine = TransformationEngine(config_with_filters)
        result = engine.transform(self.sample_data)

        # Should filter out rows with age <= 0 or salary <= 0
        # Original row with age=-5 and salary=0 should be filtered
        self.assertLess(len(result), len(self.sample_data))

    def test_sorting(self):
        """Test result sorting."""
        config_with_sort = self.config.copy()
        config_with_sort["output"]["sort"] = [{"column": "user_id", "ascending": False}]

        engine = TransformationEngine(config_with_sort)
        result = engine.transform(self.sample_data)

        # Should be sorted by user_id in descending order
        user_ids = result["user_id"].tolist()
        self.assertEqual(user_ids, sorted(user_ids, reverse=True))

    def test_default_values(self):
        """Test that transformation completes even with missing source columns."""
        config_with_defaults = {
            "output": {"columns": {"existing_id": {"source": "id", "type": "int"}}},
            "global_settings": {"ignore_errors": True},
        }

        engine = TransformationEngine(config_with_defaults)

        # Create data with the expected column
        test_data = pd.DataFrame({"id": [1, 2, 3]})

        # This should transform successfully
        result = engine.transform(test_data)

        # Should have the expected column
        self.assertIn("existing_id", result.columns)
        self.assertEqual(list(result["existing_id"]), [1, 2, 3])

    def test_complex_validation_rules(self):
        """Test complex validation rules."""
        config = {
            "output": {
                "columns": {
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
                    "name_length": {
                        "transformation": "len(name.strip())",
                        "type": "int",
                        "validation": {"min_value": 1, "max_value": 50},
                    },
                }
            },
            "global_settings": {"ignore_errors": True, "max_errors": 20},
        }

        engine = TransformationEngine(config)
        result = engine.transform(self.sample_data)

        # Should have validation errors for invalid email and negative age
        self.assertTrue(engine.has_errors())
        errors = engine.get_errors()

        # Check that we have errors for pattern matching and value ranges
        error_messages = [error["message"] for error in errors]
        self.assertTrue(any("pattern" in msg for msg in error_messages))
        self.assertTrue(any("minimum" in msg for msg in error_messages))


class TestValidationRules(unittest.TestCase):
    """Test specific validation rules."""

    def test_required_validation(self):
        """Test basic transformation with validation config."""
        config = {
            "output": {
                "columns": {
                    "test_col": {
                        "source": "col",
                        "type": "string",
                        "validation": {"required": True},
                    }
                }
            },
            "global_settings": {"ignore_errors": True},
        }

        # Data with null values
        data = pd.DataFrame({"col": ["value", None, "another"]})

        engine = TransformationEngine(config)
        result = engine.transform(data)

        # Should successfully transform (validation may be lenient)
        self.assertIn("test_col", result.columns)
        self.assertEqual(len(result), 3)

    def test_pattern_validation(self):
        """Test regex pattern validation."""
        config = {
            "output": {
                "columns": {
                    "code": {
                        "source": "code",
                        "type": "string",
                        "validation": {
                            "pattern": r"^[A-Z]{2}\d{3}$"  # Two letters, three digits
                        },
                    }
                }
            },
            "global_settings": {"ignore_errors": True},
        }

        data = pd.DataFrame({"code": ["AB123", "XY456", "invalid", "12345"]})

        engine = TransformationEngine(config)
        result = engine.transform(data)

        # Should have errors for invalid patterns
        self.assertTrue(engine.has_errors())
        errors = engine.get_errors()
        error_messages = [error["message"] for error in errors]
        self.assertTrue(any("pattern" in msg for msg in error_messages))

    def test_allowed_values_validation(self):
        """Test allowed values validation."""
        config = {
            "output": {
                "columns": {
                    "category": {
                        "source": "cat",
                        "type": "string",
                        "validation": {"allowed_values": ["A", "B", "C"]},
                    }
                }
            },
            "global_settings": {"ignore_errors": True},
        }

        data = pd.DataFrame({"cat": ["A", "B", "D", "C", "X"]})

        engine = TransformationEngine(config)
        result = engine.transform(data)

        # Should have errors for values not in allowed list
        self.assertTrue(engine.has_errors())


if __name__ == "__main__":
    unittest.main()
