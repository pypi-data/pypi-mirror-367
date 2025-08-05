"""Tests for configuration parser."""

import unittest
import tempfile
import yaml
from datatidy.config.parser import ConfigParser
from datatidy.config.schema import ConfigSchema


class TestConfigParser(unittest.TestCase):
    """Test cases for ConfigParser."""

    def setUp(self):
        """Set up test fixtures."""
        self.valid_config = {
            "input": {"type": "csv", "source": "test.csv"},
            "output": {"columns": {"test_col": {"source": "col1", "type": "string"}}},
        }

        self.invalid_config = {"input": {"type": "invalid_type", "source": "test.csv"}}

    def test_parse_dict_valid(self):
        """Test parsing valid config dictionary."""
        parser = ConfigParser()
        result = parser.parse_dict(self.valid_config)

        self.assertIn("input", result)
        self.assertIn("output", result)
        self.assertEqual(result["input"]["type"], "csv")

    def test_parse_dict_invalid(self):
        """Test parsing invalid config dictionary."""
        parser = ConfigParser()
        with self.assertRaises(ValueError):
            parser.parse_dict(self.invalid_config)

    def test_parse_string_valid(self):
        """Test parsing valid YAML string."""
        yaml_string = yaml.dump(self.valid_config)
        parser = ConfigParser()
        result = parser.parse_string(yaml_string)

        self.assertEqual(result["input"]["type"], "csv")

    def test_parse_string_invalid_yaml(self):
        """Test parsing invalid YAML string."""
        invalid_yaml = "invalid: yaml: content: ["
        parser = ConfigParser()
        with self.assertRaises(ValueError):
            parser.parse_string(invalid_yaml)

    def test_parse_file_valid(self):
        """Test parsing valid config file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(self.valid_config, f)
            temp_path = f.name

        try:
            parser = ConfigParser()
            result = parser.parse_file(temp_path)
            self.assertEqual(result["input"]["type"], "csv")
        finally:
            import os

            os.unlink(temp_path)

    def test_parse_file_not_found(self):
        """Test parsing non-existent file."""
        parser = ConfigParser()
        with self.assertRaises(FileNotFoundError):
            parser.parse_file("non_existent_file.yaml")

    def test_validate_config_valid(self):
        """Test validating valid configuration."""
        parser = ConfigParser()
        # Should not raise exception
        parser.validate_config(self.valid_config)

    def test_validate_config_invalid(self):
        """Test validating invalid configuration."""
        parser = ConfigParser()
        with self.assertRaises(ValueError):
            parser.validate_config(self.invalid_config)

    def test_process_config_defaults(self):
        """Test config processing with defaults."""
        parser = ConfigParser()

        # Create config without source to test defaults
        config_for_defaults = {
            "input": {"type": "csv", "source": "test.csv"},
            "output": {
                "columns": {
                    "test_col": {
                        "type": "string"
                        # No source specified - should default to column name
                    }
                }
            },
        }

        result = parser._process_config(config_for_defaults)

        # Check global settings defaults
        self.assertIn("global_settings", result)
        self.assertEqual(result["global_settings"]["ignore_errors"], False)
        self.assertEqual(result["global_settings"]["max_errors"], 100)

        # Check column defaults
        column_config = result["output"]["columns"]["test_col"]
        self.assertEqual(
            column_config["source"], "test_col"
        )  # Should default to column name
        self.assertIn("validation", column_config)
        self.assertEqual(column_config["validation"]["required"], True)

    def test_create_sample_config(self):
        """Test sample config creation."""
        sample = ConfigParser.create_sample_config()

        self.assertIn("input", sample)
        self.assertIn("output", sample)
        self.assertIn("global_settings", sample)

        # Validate sample config
        parser = ConfigParser()
        parser.validate_config(sample)  # Should not raise


class TestConfigSchema(unittest.TestCase):
    """Test cases for ConfigSchema."""

    def test_get_schema(self):
        """Test getting schema."""
        schema = ConfigSchema.get_schema()

        self.assertIn("properties", schema)
        self.assertIn("input", schema["properties"])
        self.assertIn("output", schema["properties"])
        # Schema uses oneOf instead of top-level required
        self.assertIn("oneOf", schema)


if __name__ == "__main__":
    unittest.main()
