"""Core DataTidy class for orchestrating data processing."""

from typing import Any, Dict, Optional, Union, Callable, List
import pandas as pd
from .config.parser import ConfigParser
from .input.readers import DataReaderFactory
from .transformation.engine import TransformationEngine
from .join_engine import JoinEngine
from .fallback.processor import FallbackProcessor, ProcessingResult
from .fallback.logger import EnhancedLogger, ProcessingMode
from .fallback.metrics import DataQualityMetrics, DataQualityComparison


class DataTidy:
    """Main class for configuration-driven data processing."""

    def __init__(self, config: Optional[Union[str, Dict[str, Any]]] = None):
        """Initialize DataTidy with optional configuration."""
        self.config_parser = ConfigParser()
        self.config: Optional[Dict[str, Any]] = None
        self.transformation_engine: Optional[TransformationEngine] = None
        self.fallback_processor: Optional[FallbackProcessor] = None
        self.logger: Optional[EnhancedLogger] = None
        self.last_processing_result: Optional[ProcessingResult] = None

        if config:
            self.load_config(config)

    def load_config(self, config: Union[str, Dict[str, Any]]) -> None:
        """Load configuration from file path or dictionary."""
        if isinstance(config, str):
            self.config = self.config_parser.parse_file(config)
        elif isinstance(config, dict):
            self.config = self.config_parser.parse_dict(config)
        else:
            raise ValueError("Config must be a file path string or dictionary")

        # Initialize transformation engine with loaded config
        self.transformation_engine = TransformationEngine(self.config)

        # Initialize fallback processor and enhanced logger
        self.logger = EnhancedLogger()
        self.fallback_processor = FallbackProcessor(self.config, self.logger)

    def load_config_from_string(self, config_string: str) -> None:
        """Load configuration from YAML string."""
        self.config = self.config_parser.parse_string(config_string)
        self.transformation_engine = TransformationEngine(self.config)
        self.logger = EnhancedLogger()
        self.fallback_processor = FallbackProcessor(self.config, self.logger)

    def process_data(
        self, data: Optional[Union[str, pd.DataFrame]] = None
    ) -> pd.DataFrame:
        """Process data according to configuration."""
        if not self.config:
            raise ValueError("No configuration loaded. Call load_config() first.")

        # Load input data if not provided
        if data is None:
            input_df = self._load_input_data()
        elif isinstance(data, pd.DataFrame):
            input_df = data
        elif isinstance(data, str):
            # Treat as file path and load according to config
            input_df = self._load_data_from_path(data)
        else:
            raise ValueError("Data must be a pandas DataFrame, file path, or None")

        # Apply transformations
        if not self.transformation_engine:
            raise ValueError("Transformation engine not initialized")

        result_df = self.transformation_engine.transform(input_df)

        return result_df

    def process_data_with_fallback(
        self,
        data: Optional[Union[str, pd.DataFrame]] = None,
        fallback_query_func: Optional[Callable] = None,
    ) -> ProcessingResult:
        """
        Process data with enhanced fallback capabilities.

        Args:
            data: Input data (DataFrame, file path, or None to use config input)
            fallback_query_func: Optional function to call for fallback data loading

        Returns:
            ProcessingResult with detailed processing information
        """
        if not self.config:
            raise ValueError("No configuration loaded. Call load_config() first.")

        # Load input data if not provided
        if data is None:
            input_df = self._load_input_data()
        elif isinstance(data, pd.DataFrame):
            input_df = data
        elif isinstance(data, str):
            input_df = self._load_data_from_path(data)
        else:
            raise ValueError("Data must be a pandas DataFrame, file path, or None")

        # Process with fallback capabilities
        if not self.fallback_processor:
            raise ValueError("Fallback processor not initialized")

        result = self.fallback_processor.process_with_fallback(
            input_df, self.transformation_engine, fallback_query_func
        )

        self.last_processing_result = result
        return result

    def get_processing_summary(self) -> Dict[str, Any]:
        """Get summary of the last processing operation."""
        if not self.last_processing_result:
            return {"error": "No processing operation completed yet"}

        result = self.last_processing_result
        return {
            "success": result.success,
            "processing_mode": result.processing_mode.value,
            "processing_time": result.processing_time,
            "total_columns": (
                len(self.config["output"]["columns"]) if self.config else 0
            ),
            "successful_columns": len(result.successful_columns),
            "failed_columns": len(result.failed_columns),
            "skipped_columns": len(result.skipped_columns),
            "fallback_used": result.fallback_used,
            "error_count": len(result.error_log),
        }

    def get_error_report(self) -> Optional[Dict[str, Any]]:
        """Get detailed error report from the last processing operation."""
        if not self.logger:
            return None
        return self.logger.get_error_report()

    def get_processing_recommendations(self) -> List[str]:
        """Get recommendations for improving processing success."""
        if not self.fallback_processor:
            return ["Initialize fallback processor first"]
        return self.fallback_processor.get_processing_recommendations()

    def compare_with_fallback(self, fallback_df: pd.DataFrame) -> DataQualityComparison:
        """
        Compare DataTidy results with fallback results.

        Args:
            fallback_df: DataFrame from fallback processing

        Returns:
            DataQualityComparison object with detailed metrics
        """
        if not self.last_processing_result:
            raise ValueError("No DataTidy processing result available for comparison")

        return DataQualityMetrics.compare_results(
            self.last_processing_result.data,
            fallback_df,
            self.last_processing_result.processing_time,
            0,  # Fallback time not tracked in this context
        )

    def export_error_log(self, file_path: str):
        """Export error log to JSON file."""
        if self.logger:
            self.logger.export_error_log(file_path)
        else:
            raise ValueError("Logger not initialized")

    def set_processing_mode(self, mode: Union[str, ProcessingMode]):
        """Set the processing mode for fallback processor."""
        if isinstance(mode, str):
            mode = ProcessingMode(mode)

        if self.fallback_processor:
            self.fallback_processor.processing_mode = mode
        else:
            raise ValueError("Fallback processor not initialized")

    def process_and_save(
        self,
        output_path: str,
        data: Optional[Union[str, pd.DataFrame]] = None,
        **kwargs: Any,
    ) -> None:
        """Process data and save to file."""
        result_df = self.process_data(data)

        # Determine output format from file extension
        if output_path.endswith(".csv"):
            result_df.to_csv(output_path, index=False, **kwargs)
        elif output_path.endswith((".xlsx", ".xls")):
            result_df.to_excel(output_path, index=False, **kwargs)
        elif output_path.endswith(".json"):
            result_df.to_json(output_path, **kwargs)
        elif output_path.endswith(".parquet"):
            result_df.to_parquet(output_path, **kwargs)
        else:
            # Default to CSV
            result_df.to_csv(output_path, index=False, **kwargs)

    def get_errors(self) -> list:
        """Get processing errors from transformation engine."""
        if self.transformation_engine:
            return self.transformation_engine.get_errors()
        return []

    def has_errors(self) -> bool:
        """Check if there are processing errors."""
        if self.transformation_engine:
            return self.transformation_engine.has_errors()
        return False

    def _load_input_data(self) -> pd.DataFrame:
        """Load input data based on configuration."""
        # Check if using new multi-input format
        if self.config and "inputs" in self.config:
            return self._load_multi_input_data()

        # Single input (backward compatibility)
        if not self.config:
            raise ValueError("No configuration loaded")
        input_config = self.config["input"]
        source_type = input_config["type"]
        source = input_config["source"]

        # Get additional options
        connection_string = input_config.get("connection_string")
        options = input_config.get("options", {})

        # Create appropriate reader
        reader = DataReaderFactory.get_reader(
            source_type, connection_string=connection_string
        )

        # Read data
        return reader.read(source, **options)

    def _load_multi_input_data(self) -> pd.DataFrame:
        """Load and join multiple input sources."""
        if not self.config:
            raise ValueError("No configuration loaded")
        inputs_config = self.config["inputs"]
        joins_config = self.config.get("joins", [])

        # Initialize join engine
        join_engine = JoinEngine()

        # Load all input datasets
        for name, input_config in inputs_config.items():
            source_type = input_config["type"]
            source = input_config["source"]
            connection_string = input_config.get("connection_string")
            options = input_config.get("options", {})

            # Create appropriate reader
            reader = DataReaderFactory.get_reader(
                source_type, connection_string=connection_string
            )

            # Read data and add to join engine
            df = reader.read(source, **options)
            join_engine.add_dataset(name, df)

        # Perform joins if specified
        if joins_config:
            return join_engine.perform_joins(joins_config)
        else:
            # No joins - return first dataset if only one, otherwise error
            datasets = join_engine.get_available_datasets()
            if len(datasets) == 1:
                return list(join_engine.datasets.values())[0]
            else:
                raise ValueError("Multiple inputs provided but no joins specified")

    def _load_data_from_path(self, file_path: str) -> pd.DataFrame:
        """Load data from file path using appropriate reader."""
        # Determine file type from extension
        if file_path.endswith(".csv"):
            source_type = "csv"
        elif file_path.endswith((".xlsx", ".xls")):
            source_type = "excel"
        elif file_path.endswith(".parquet"):
            source_type = "parquet"
        elif file_path.endswith(".pkl"):
            source_type = "pickle"
        else:
            raise ValueError(f"Unsupported file type for path: {file_path}")

        reader = DataReaderFactory.get_reader(source_type)
        return reader.read(file_path)

    @staticmethod
    def create_sample_config(output_path: str) -> None:
        """Create a sample configuration file."""
        sample_config = ConfigParser.create_sample_config()

        import yaml

        with open(output_path, "w", encoding="utf-8") as f:
            yaml.dump(sample_config, f, default_flow_style=False, indent=2)

    def validate_config(self) -> bool:
        """Validate the current configuration."""
        if not self.config:
            return False

        try:
            self.config_parser.validate_config(self.config)
            return True
        except ValueError:
            return False

    def get_config(self) -> Optional[Dict[str, Any]]:
        """Get the current configuration."""
        return self.config
