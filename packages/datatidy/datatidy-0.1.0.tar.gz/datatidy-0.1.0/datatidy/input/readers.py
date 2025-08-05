"""Data readers for various input sources."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


class DataReader(ABC):
    """Base class for all data readers."""

    @abstractmethod
    def read(self, source: Union[str, Dict[str, Any]], **kwargs: Any) -> pd.DataFrame:
        """Read data from source and return as pandas DataFrame."""
        pass


class CSVReader(DataReader):
    """Reader for CSV files."""

    def read(self, source: Union[str, Dict[str, Any]], **kwargs: Any) -> pd.DataFrame:
        """Read CSV file and return DataFrame."""
        if isinstance(source, dict):
            file_path = source.get("path", "")
            csv_options = source.get("options", {})
        else:
            file_path = source
            csv_options = {}

        # Merge kwargs with csv_options, with kwargs taking precedence
        options = {**csv_options, **kwargs}

        return pd.read_csv(file_path, **options)


class ExcelReader(DataReader):
    """Reader for Excel files."""

    def read(self, source: Union[str, Dict[str, Any]], **kwargs: Any) -> pd.DataFrame:
        """Read Excel file and return DataFrame."""
        if isinstance(source, dict):
            file_path = source.get("path", "")
            sheet_name = source.get("sheet_name", 0)
            excel_options = source.get("options", {})
        else:
            file_path = source
            sheet_name = kwargs.pop("sheet_name", 0)
            excel_options = {}

        # Merge kwargs with excel_options, with kwargs taking precedence
        options = {**excel_options, **kwargs}

        return pd.read_excel(file_path, sheet_name=sheet_name, **options)


class DatabaseReader(DataReader):
    """Reader for database sources."""

    def __init__(self, connection_string: Optional[str] = None):
        """Initialize with optional connection string."""
        self.connection_string = connection_string
        self._engine: Optional[Engine] = None

    @property
    def engine(self) -> Engine:
        """Get or create SQLAlchemy engine."""
        if self._engine is None:
            if not self.connection_string:
                raise ValueError("Connection string is required")
            self._engine = create_engine(self.connection_string)
        return self._engine

    def read(self, source: Union[str, Dict[str, Any]], **kwargs: Any) -> pd.DataFrame:
        """Read from database and return DataFrame."""
        if isinstance(source, dict):
            query = source.get("query", "")
            connection_string = source.get("connection_string")
            db_options = source.get("options", {})
        else:
            query = source
            connection_string = None
            db_options = {}

        # Use provided connection string or fall back to instance connection string
        if connection_string:
            engine = create_engine(connection_string)
        else:
            engine = self.engine

        # Merge kwargs with db_options, with kwargs taking precedence
        options = {**db_options, **kwargs}

        return pd.read_sql(query, engine, **options)


class ParquetReader(DataReader):
    """Reader for Parquet files."""

    def read(self, source: Union[str, Dict[str, Any]], **kwargs: Any) -> pd.DataFrame:
        """Read Parquet file and return DataFrame."""
        if isinstance(source, dict):
            file_path = source.get("path", "")
            parquet_options = source.get("options", {})
        else:
            file_path = source
            parquet_options = {}

        # Merge kwargs with parquet_options, with kwargs taking precedence
        options = {**parquet_options, **kwargs}

        return pd.read_parquet(file_path, **options)


class PickleReader(DataReader):
    """Reader for Pickle files."""

    def read(self, source: Union[str, Dict[str, Any]], **kwargs: Any) -> pd.DataFrame:
        """Read Pickle file and return DataFrame."""
        if isinstance(source, dict):
            file_path = source.get("path", "")
            pickle_options = source.get("options", {})
        else:
            file_path = source
            pickle_options = {}

        # Merge kwargs with pickle_options, with kwargs taking precedence
        options = {**pickle_options, **kwargs}

        return pd.read_pickle(file_path, **options)


class DataReaderFactory:
    """Factory for creating appropriate data readers."""

    _readers = {
        "csv": CSVReader,
        "excel": ExcelReader,
        "xlsx": ExcelReader,
        "xls": ExcelReader,
        "database": DatabaseReader,
        "db": DatabaseReader,
        "sql": DatabaseReader,
        "snowflake": DatabaseReader,
        "postgres": DatabaseReader,
        "mysql": DatabaseReader,
        "parquet": ParquetReader,
        "pickle": PickleReader,
    }

    @classmethod
    def get_reader(cls, source_type: str, **kwargs: Any) -> DataReader:
        """Get appropriate reader for source type."""
        source_type = source_type.lower()

        if source_type not in cls._readers:
            raise ValueError(f"Unsupported source type: {source_type}")

        reader_class = cls._readers[source_type]

        # For database readers, pass connection_string if provided
        if issubclass(reader_class, DatabaseReader):
            connection_string = kwargs.get("connection_string")
            return reader_class(connection_string=connection_string)

        return reader_class()

    @classmethod
    def register_reader(cls, source_type: str, reader_class: type) -> None:
        """Register a new reader type."""
        cls._readers[source_type.lower()] = reader_class
