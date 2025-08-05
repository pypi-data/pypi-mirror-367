"""JSON Schema definitions for configuration validation."""

INPUT_SOURCE_SCHEMA = {
    "type": "object",
    "required": ["type", "source"],
    "properties": {
        "type": {
            "type": "string",
            "enum": [
                "csv",
                "excel",
                "xlsx",
                "xls",
                "database",
                "db",
                "sql",
                "snowflake",
                "postgres",
                "mysql",
                "parquet",
                "pickle",
            ],
        },
        "source": {
            "oneOf": [
                {"type": "string"},
                {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "query": {"type": "string"},
                        "connection_string": {"type": "string"},
                        "sheet_name": {
                            "oneOf": [{"type": "string"}, {"type": "integer"}]
                        },
                        "options": {"type": "object"},
                    },
                },
            ]
        },
        "connection_string": {"type": "string"},
        "options": {"type": "object"},
    },
}

JOIN_SCHEMA = {
    "type": "object",
    "required": ["left", "right", "on"],
    "properties": {
        "left": {"type": "string"},
        "right": {"type": "string"},
        "on": {
            "oneOf": [
                {"type": "string"},
                {"type": "array", "items": {"type": "string"}},
                {
                    "type": "object",
                    "properties": {
                        "left": {
                            "oneOf": [
                                {"type": "string"},
                                {"type": "array", "items": {"type": "string"}},
                            ]
                        },
                        "right": {
                            "oneOf": [
                                {"type": "string"},
                                {"type": "array", "items": {"type": "string"}},
                            ]
                        },
                    },
                    "required": ["left", "right"],
                },
                {
                    "type": "object",
                    "patternProperties": {
                        "^[a-zA-Z_][a-zA-Z0-9_]*$": {"type": "string"}
                    },
                },
            ]
        },
        "how": {
            "type": "string",
            "enum": ["inner", "left", "right", "outer", "cross"],
            "default": "inner",
        },
        "suffix": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 2,
            "maxItems": 2,
        },
    },
}

CONFIG_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "DataTidy Configuration Schema",
    "type": "object",
    "oneOf": [
        {"required": ["input", "output"], "properties": {"input": INPUT_SOURCE_SCHEMA}},
        {
            "required": ["inputs", "output"],
            "properties": {
                "inputs": {
                    "type": "object",
                    "patternProperties": {
                        "^[a-zA-Z_][a-zA-Z0-9_]*$": INPUT_SOURCE_SCHEMA
                    },
                    "minProperties": 1,
                },
                "joins": {"type": "array", "items": JOIN_SCHEMA},
            },
        },
    ],
    "properties": {
        "input": INPUT_SOURCE_SCHEMA,
        "inputs": {
            "type": "object",
            "patternProperties": {"^[a-zA-Z_][a-zA-Z0-9_]*$": INPUT_SOURCE_SCHEMA},
            "minProperties": 1,
        },
        "joins": {"type": "array", "items": JOIN_SCHEMA},
        "output": {
            "type": "object",
            "required": ["columns"],
            "properties": {
                "only_output_columns": {"type": "boolean", "default": False},
                "columns": {
                    "type": "object",
                    "patternProperties": {
                        "^[a-zA-Z_][a-zA-Z0-9_]*$": {
                            "type": "object",
                            "properties": {
                                "source": {"type": "string"},
                                "type": {
                                    "type": "string",
                                    "enum": [
                                        "string",
                                        "int",
                                        "float",
                                        "bool",
                                        "datetime",
                                    ],
                                },
                                "format": {"type": "string"},
                                "transformation": {"type": "string"},
                                "interim": {"type": "boolean", "default": False},
                                "operations": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "type": {
                                                "type": "string",
                                                "enum": [
                                                    "map",
                                                    "filter",
                                                    "reduce",
                                                    "group",
                                                    "window",
                                                ],
                                            },
                                            "function": {"type": "string"},
                                            "condition": {"type": "string"},
                                            "fill_value": {},
                                            "initial_value": {},
                                            "group_by": {"type": "string"},
                                            "window_size": {"type": "integer"},
                                        },
                                        "required": ["type"],
                                    },
                                },
                                "validation": {
                                    "type": "object",
                                    "properties": {
                                        "required": {"type": "boolean"},
                                        "nullable": {"type": "boolean"},
                                        "min_value": {"type": "number"},
                                        "max_value": {"type": "number"},
                                        "min_length": {"type": "integer"},
                                        "max_length": {"type": "integer"},
                                        "pattern": {"type": "string"},
                                        "allowed_values": {"type": "array"},
                                    },
                                },
                                "default": {},
                            },
                        }
                    },
                },
                "filters": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["condition"],
                        "properties": {
                            "condition": {"type": "string"},
                            "action": {
                                "type": "string",
                                "enum": ["keep", "remove"],
                                "default": "keep",
                            },
                        },
                    },
                },
                "sort": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["column"],
                        "properties": {
                            "column": {"type": "string"},
                            "ascending": {"type": "boolean", "default": True},
                        },
                    },
                },
            },
        },
        "global_settings": {
            "type": "object",
            "properties": {
                "ignore_errors": {"type": "boolean", "default": False},
                "max_errors": {"type": "integer", "default": 100},
                "encoding": {"type": "string", "default": "utf-8"},
                "show_execution_plan": {"type": "boolean", "default": False},
                "verbose": {"type": "boolean", "default": False},
            },
        },
    },
}


class ConfigSchema:
    """Configuration schema validator."""

    @staticmethod
    def get_schema() -> dict:
        """Get the configuration schema."""
        return CONFIG_SCHEMA
