"""Tests for data readers."""

import unittest
import pandas as pd
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from datatidy.input.readers import (
    CSVReader,
    ExcelReader,
    DatabaseReader,
    DataReaderFactory,
)


class TestCSVReader(unittest.TestCase):
    """Test cases for CSVReader."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_data = pd.DataFrame(
            {"id": [1, 2, 3], "name": ["Alice", "Bob", "Charlie"], "age": [25, 30, 35]}
        )

        # Create temporary CSV file
        self.temp_csv = tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        )
        self.test_data.to_csv(self.temp_csv.name, index=False)
        self.temp_csv.close()

    def tearDown(self):
        """Clean up."""
        os.unlink(self.temp_csv.name)

    def test_read_string_source(self):
        """Test reading CSV with string source."""
        reader = CSVReader()
        result = reader.read(self.temp_csv.name)

        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 3)
        self.assertListEqual(list(result.columns), ["id", "name", "age"])

    def test_read_dict_source(self):
        """Test reading CSV with dictionary source."""
        reader = CSVReader()
        source = {"path": self.temp_csv.name, "options": {"sep": ","}}
        result = reader.read(source)

        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 3)

    def test_read_with_kwargs(self):
        """Test reading CSV with additional kwargs."""
        reader = CSVReader()
        result = reader.read(self.temp_csv.name, encoding="utf-8")

        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 3)


class TestExcelReader(unittest.TestCase):
    """Test cases for ExcelReader."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_data = pd.DataFrame(
            {"id": [1, 2, 3], "name": ["Alice", "Bob", "Charlie"], "age": [25, 30, 35]}
        )

        # Create temporary Excel file
        self.temp_excel = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
        self.temp_excel.close()
        self.test_data.to_excel(self.temp_excel.name, index=False)

    def tearDown(self):
        """Clean up."""
        os.unlink(self.temp_excel.name)

    def test_read_string_source(self):
        """Test reading Excel with string source."""
        reader = ExcelReader()
        result = reader.read(self.temp_excel.name)

        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 3)
        self.assertListEqual(list(result.columns), ["id", "name", "age"])

    def test_read_dict_source(self):
        """Test reading Excel with dictionary source."""
        reader = ExcelReader()
        source = {"path": self.temp_excel.name, "sheet_name": 0, "options": {}}
        result = reader.read(source)

        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 3)


class TestDatabaseReader(unittest.TestCase):
    """Test cases for DatabaseReader."""

    @patch("datatidy.input.readers.create_engine")
    @patch("pandas.read_sql")
    def test_read_string_source(self, mock_read_sql, mock_create_engine):
        """Test reading from database with string source."""
        # Mock setup
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        mock_read_sql.return_value = pd.DataFrame({"col": [1, 2, 3]})

        reader = DatabaseReader("sqlite:///test.db")
        result = reader.read("SELECT * FROM test")

        self.assertIsInstance(result, pd.DataFrame)
        mock_read_sql.assert_called_once()

    @patch("datatidy.input.readers.create_engine")
    @patch("pandas.read_sql")
    def test_read_dict_source(self, mock_read_sql, mock_create_engine):
        """Test reading from database with dictionary source."""
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        mock_read_sql.return_value = pd.DataFrame({"col": [1, 2, 3]})

        reader = DatabaseReader()
        source = {
            "query": "SELECT * FROM test",
            "connection_string": "sqlite:///test.db",
        }
        result = reader.read(source)

        self.assertIsInstance(result, pd.DataFrame)
        mock_read_sql.assert_called_once()

    def test_no_connection_string(self):
        """Test error when no connection string provided."""
        reader = DatabaseReader()
        with self.assertRaises(ValueError):
            reader.read("SELECT * FROM test")


class TestDataReaderFactory(unittest.TestCase):
    """Test cases for DataReaderFactory."""

    def test_get_csv_reader(self):
        """Test getting CSV reader."""
        reader = DataReaderFactory.get_reader("csv")
        self.assertIsInstance(reader, CSVReader)

    def test_get_excel_reader(self):
        """Test getting Excel reader."""
        reader = DataReaderFactory.get_reader("excel")
        self.assertIsInstance(reader, ExcelReader)

        reader = DataReaderFactory.get_reader("xlsx")
        self.assertIsInstance(reader, ExcelReader)

    def test_get_database_reader(self):
        """Test getting database reader."""
        reader = DataReaderFactory.get_reader("database")
        self.assertIsInstance(reader, DatabaseReader)

        reader = DataReaderFactory.get_reader(
            "postgres", connection_string="postgresql://test"
        )
        self.assertIsInstance(reader, DatabaseReader)

    def test_unsupported_type(self):
        """Test error for unsupported reader type."""
        with self.assertRaises(ValueError):
            DataReaderFactory.get_reader("unsupported_type")

    def test_register_reader(self):
        """Test registering custom reader."""

        class CustomReader:
            pass

        DataReaderFactory.register_reader("custom", CustomReader)
        reader = DataReaderFactory.get_reader("custom")
        self.assertIsInstance(reader, CustomReader)


if __name__ == "__main__":
    unittest.main()
