DataTidy Documentation
======================

**DataTidy** is a powerful, configuration-driven data processing and cleaning package for Python with robust fallback capabilities. It allows you to define complex data transformations, validations, and cleanings through simple YAML configuration files, ensuring 100% reliability in production environments.

.. image:: https://img.shields.io/badge/version-0.1.0-blue.svg
   :target: https://github.com/wwd1015/datatidy
   :alt: Version

.. image:: https://img.shields.io/badge/python-3.8+-blue.svg
   :target: https://www.python.org/downloads/
   :alt: Python Version

.. image:: https://img.shields.io/badge/license-MIT-green.svg
   :target: https://opensource.org/licenses/MIT
   :alt: License

Key Features
------------

* **🔧 Configuration-Driven**: Define all transformations in YAML - no code required
* **📊 Multiple Data Sources**: CSV, Excel, databases (PostgreSQL, MySQL, Snowflake, etc.)
* **🔗 Multi-Input Joins**: Combine data from multiple sources with flexible join operations
* **⚡ Advanced Operations**: Map/reduce/filter with lambda functions and chained operations
* **🧠 Dependency Resolution**: Automatic execution order planning for complex transformations
* **🛡️ Safe Expressions**: Secure evaluation with whitelist-based security
* **🎯 Data Validation**: Comprehensive validation rules with detailed error reporting

Enhanced Fallback System (v0.1.0)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **🛡️ 100% Reliability**: Dashboard never fails to load data with automatic fallback mechanisms
* **⚖️ Graceful Degradation**: Gets sophisticated transformations when possible, basic data when needed
* **🔍 Enhanced Error Logging**: Detailed error categorization with actionable debugging suggestions
* **📊 Data Quality Metrics**: Compare DataTidy results with fallback data for quality assessment
* **🎛️ Multiple Processing Modes**: Strict, partial, and fallback modes for different reliability requirements
* **🔧 Partial Processing**: Skip problematic columns while processing successful ones
* **📋 Processing Recommendations**: Get specific suggestions for improving configurations

Quick Start
-----------

Installation
~~~~~~~~~~~~

.. code-block:: bash

   pip install datatidy

Basic Usage
~~~~~~~~~~~

.. code-block:: python

   from datatidy import DataTidy

   # Initialize with configuration
   dt = DataTidy('config.yaml')

   # Standard processing
   result = dt.process_data('input.csv')

   # Enhanced processing with fallback
   result = dt.process_data_with_fallback('input.csv')

   # Production-ready processing with database fallback
   def fallback_query():
       return pd.read_sql("SELECT * FROM facilities", db_connection)
   
   result = dt.process_data_with_fallback(
       data=input_df,
       fallback_query_func=fallback_query
   )

   # Your application always gets data!
   if result.fallback_used:
       logger.warning("DataTidy processing failed, using database fallback")

Command Line Interface
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Strict mode (default) - fails on any error
   datatidy process config.yaml --mode strict

   # Partial mode - skip problematic columns
   datatidy process config.yaml --mode partial --show-summary

   # Fallback mode - use fallback transformations
   datatidy process config.yaml --mode fallback

   # Development mode with detailed feedback
   datatidy process config.yaml --mode partial \\
     --show-summary \\
     --show-recommendations \\
     --error-log debug.json

Performance
-----------

The enhanced fallback system provides **100% reliability** with **virtually zero performance overhead**:

* **Average overhead**: -0.1% (actually slightly faster!)
* **Performance range**: -0.3% to +0.3%
* **Consistent across data sizes**: 1K to 500K+ rows
* **Memory efficient**: No leaks detected

See :doc:`performance` for detailed benchmark results.

Table of Contents
-----------------

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   installation
   quickstart
   configuration
   fallback_system
   performance
   examples

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/core
   api/fallback
   api/config
   api/transformation
   api/input
   api/cli

.. toctree::
   :maxdepth: 1
   :caption: Development

   contributing
   changelog

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`