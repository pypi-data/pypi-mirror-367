"""Configuration parser for YAML files."""

from typing import Any, Dict
import yaml
import jsonschema
from .schema import ConfigSchema


class ConfigParser:
    """Parser for YAML configuration files."""

    def __init__(self, validate: bool = True):
        """Initialize parser with optional validation."""
        self.validate = validate
        self.schema = ConfigSchema.get_schema()

    def parse_file(self, config_path: str) -> Dict[str, Any]:
        """Parse configuration from YAML file."""
        try:
            with open(config_path, "r", encoding="utf-8") as file:
                config = yaml.safe_load(file)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML syntax: {e}")
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        if self.validate:
            self.validate_config(config)

        return self._process_config(config)

    def parse_string(self, config_string: str) -> Dict[str, Any]:
        """Parse configuration from YAML string."""
        try:
            config = yaml.safe_load(config_string)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML syntax: {e}")

        if self.validate:
            self.validate_config(config)

        return self._process_config(config)

    def parse_dict(self, config_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Parse configuration from dictionary."""
        if self.validate:
            self.validate_config(config_dict)

        return self._process_config(config_dict)

    def validate_config(self, config: Dict[str, Any]) -> None:
        """Validate configuration against schema."""
        try:
            jsonschema.validate(config, self.schema)
        except jsonschema.ValidationError as e:
            raise ValueError(f"Configuration validation error: {e.message}")

    def _process_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Process and normalize configuration."""
        # Set default values
        config.setdefault("global_settings", {})
        global_settings = config["global_settings"]
        global_settings.setdefault("ignore_errors", False)
        global_settings.setdefault("max_errors", 100)
        global_settings.setdefault("encoding", "utf-8")

        # Process output columns
        output_columns = config["output"]["columns"]
        for column_name, column_config in output_columns.items():
            # Set default column properties
            column_config.setdefault("type", "string")
            column_config.setdefault("source", column_name)

            # Set default validation rules
            if "validation" not in column_config:
                column_config["validation"] = {}

            validation = column_config["validation"]
            validation.setdefault("required", True)
            validation.setdefault("nullable", False)

        # Process filters
        if "filters" in config["output"]:
            for filter_config in config["output"]["filters"]:
                filter_config.setdefault("action", "keep")

        # Process sorting
        if "sort" in config["output"]:
            for sort_config in config["output"]["sort"]:
                sort_config.setdefault("ascending", True)

        return config

    @staticmethod
    def create_sample_config() -> Dict[str, Any]:
        """Create a sample configuration for reference."""
        return {
            "input": {
                "type": "csv",
                "source": "data/input.csv",
                "options": {"encoding": "utf-8", "delimiter": ","},
            },
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
                        "transformation": "str.title()",
                        "validation": {
                            "required": True,
                            "min_length": 2,
                            "max_length": 100,
                        },
                    },
                    "email": {
                        "source": "email_address",
                        "type": "string",
                        "validation": {
                            "required": True,
                            "pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
                        },
                    },
                    "age_group": {
                        "transformation": "'adult' if age >= 18 else 'minor'",
                        "type": "string",
                        "validation": {"allowed_values": ["adult", "minor"]},
                    },
                },
                "filters": [{"condition": "age >= 0", "action": "keep"}],
                "sort": [{"column": "user_id", "ascending": True}],
            },
            "global_settings": {
                "ignore_errors": False,
                "max_errors": 50,
                "encoding": "utf-8",
            },
        }
