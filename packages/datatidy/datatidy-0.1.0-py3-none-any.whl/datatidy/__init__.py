"""
DataTidy: A configuration-driven data processing and cleaning package with robust fallback capabilities.

This package provides a unified interface for data processing tasks through
YAML configuration files. It supports multiple input sources including
CSV files, Excel files, and various databases.

Key Features:
- Configuration-driven data transformations
- Robust fallback processing with partial processing modes
- Enhanced error logging and categorization
- Data quality metrics and comparison
- Multiple processing modes (strict, partial, fallback)
- Integration with external data sources and queries

Example:
    >>> from datatidy import DataTidy
    >>> dt = DataTidy('config.yaml')
    >>>
    >>> # Standard processing
    >>> result_df = dt.process_data()
    >>>
    >>> # Enhanced processing with fallback
    >>> result = dt.process_data_with_fallback(fallback_query_func=database_query)
    >>> if result.fallback_used:
    >>>     print("Fallback processing was used")
"""

from .core import DataTidy
from .config.parser import ConfigParser
from .input.readers import DataReader
from .fallback.processor import FallbackProcessor, ProcessingResult
from .fallback.logger import EnhancedLogger, ProcessingMode, ErrorCategory
from .fallback.metrics import DataQualityMetrics, DataQualityComparison

__version__ = "0.1.0"
__all__ = [
    "DataTidy",
    "ConfigParser",
    "DataReader",
    "FallbackProcessor",
    "ProcessingResult",
    "EnhancedLogger",
    "ProcessingMode",
    "ErrorCategory",
    "DataQualityMetrics",
    "DataQualityComparison",
]
