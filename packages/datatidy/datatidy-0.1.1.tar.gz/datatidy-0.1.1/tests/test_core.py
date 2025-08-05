"""Tests for the core DataTidy functionality."""

import unittest
import pandas as pd
import tempfile
import os
from pathlib import Path

from datatidy import DataTidy
from datatidy.core import DataTidy as DataTidyCore


class TestDataTidy(unittest.TestCase):
    """Test cases for DataTidy class."""

    def setUp(self):
        """Set up test fixtures."""
        self.sample_config = {
            "input": {"type": "csv", "source": "test_data.csv"},
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
                }
            },
            "global_settings": {"ignore_errors": True, "max_errors": 10},
        }

        # Create sample data
        self.sample_data = pd.DataFrame(
            {
                "id": [1, 2, 3, 4],
                "name": [" John Doe ", "Jane Smith", " Bob Wilson", "Alice Brown "],
                "age": [25, 17, 45, 30],
                "email": [
                    "john@test.com",
                    "jane@test.com",
                    "bob@test.com",
                    "alice@test.com",
                ],
            }
        )

    def test_init_with_config_dict(self):
        """Test initialization with config dictionary."""
        dt = DataTidy(self.sample_config)
        self.assertIsNotNone(dt.config)
        self.assertIsNotNone(dt.transformation_engine)

    def test_init_without_config(self):
        """Test initialization without config."""
        dt = DataTidy()
        self.assertIsNone(dt.config)
        self.assertIsNone(dt.transformation_engine)

    def test_load_config_dict(self):
        """Test loading config from dictionary."""
        dt = DataTidy()
        dt.load_config(self.sample_config)
        self.assertIsNotNone(dt.config)
        self.assertEqual(dt.config["input"]["type"], "csv")

    def test_process_data_with_dataframe(self):
        """Test processing with pandas DataFrame input."""
        dt = DataTidy(self.sample_config)
        result = dt.process_data(self.sample_data)

        # Check result is a DataFrame
        self.assertIsInstance(result, pd.DataFrame)
        self.assertIn("user_id", result.columns)
        self.assertIn("full_name", result.columns)
        self.assertIn("age_group", result.columns)

        # Check transformations
        self.assertEqual(result.iloc[0]["full_name"], "John Doe")
        self.assertEqual(result.iloc[1]["age_group"], "minor")
        self.assertEqual(result.iloc[2]["age_group"], "adult")

    def test_validation_errors(self):
        """Test validation error handling."""
        # Create data with validation errors
        bad_data = pd.DataFrame(
            {
                "id": [0, -1, 2],  # Invalid IDs (< 1)
                "name": ["A", "", "Valid Name"],  # Too short names
                "age": [25, 17, 45],
            }
        )

        dt = DataTidy(self.sample_config)
        result = dt.process_data(bad_data)

        # Should still return a DataFrame (errors ignored due to ignore_errors=True)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertGreater(len(result), 0)

    def test_create_sample_config(self):
        """Test sample config creation."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            temp_path = f.name

        try:
            DataTidy.create_sample_config(temp_path)
            self.assertTrue(os.path.exists(temp_path))

            # Load and verify it's valid YAML
            dt = DataTidy()
            dt.load_config(temp_path)
            self.assertTrue(dt.validate_config())
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_process_and_save_csv(self):
        """Test processing and saving to CSV."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            temp_path = f.name

        try:
            dt = DataTidy(self.sample_config)
            result = dt.process_and_save(temp_path, self.sample_data)

            self.assertTrue(os.path.exists(temp_path))

            # Verify output
            result_df = pd.read_csv(temp_path)
            self.assertIn("user_id", result_df.columns)
            self.assertIn("full_name", result_df.columns)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_get_config(self):
        """Test getting current configuration."""
        dt = DataTidy(self.sample_config)
        config = dt.get_config()
        self.assertEqual(config, dt.config)
        self.assertEqual(config["input"]["type"], "csv")


class TestDataTidyIntegration(unittest.TestCase):
    """Integration tests for DataTidy with real files."""

    def setUp(self):
        """Set up test files."""
        self.test_dir = Path(__file__).parent
        self.sample_csv = self.test_dir / "sample_test_data.csv"

        # Create test CSV
        test_data = pd.DataFrame(
            {
                "id": [1, 2, 3],
                "name": [" Test User 1 ", "Test User 2", " Test User 3"],
                "age": [25, 35, 45],
                "salary": [50000, 75000, 100000],
            }
        )
        test_data.to_csv(self.sample_csv, index=False)

    def tearDown(self):
        """Clean up test files."""
        if self.sample_csv.exists():
            self.sample_csv.unlink()

    def test_file_processing(self):
        """Test processing actual CSV file."""
        config = {
            "input": {"type": "csv", "source": str(self.sample_csv)},
            "output": {
                "columns": {
                    "user_id": {"source": "id", "type": "int"},
                    "clean_name": {
                        "source": "name",
                        "transformation": "name.strip().title()",
                        "type": "string",
                    },
                    "salary_bracket": {
                        "transformation": "'high' if salary > 80000 else ('medium' if salary > 60000 else 'low')",
                        "type": "string",
                    },
                }
            },
        }

        dt = DataTidy(config)
        result = dt.process_data()

        # Check processing returned a DataFrame
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 3)
        self.assertEqual(result.iloc[0]["clean_name"], "Test User 1")
        self.assertEqual(result.iloc[0]["salary_bracket"], "low")
        self.assertEqual(result.iloc[2]["salary_bracket"], "high")


if __name__ == "__main__":
    unittest.main()
