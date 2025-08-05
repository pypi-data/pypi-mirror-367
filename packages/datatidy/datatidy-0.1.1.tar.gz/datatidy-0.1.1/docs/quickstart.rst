Quick Start Guide
=================

This guide will get you up and running with DataTidy in minutes, including the enhanced fallback system for production environments.

Basic Concepts
--------------

DataTidy is a configuration-driven data processing package that:

* **Transforms data** using YAML configuration files
* **Validates data** with comprehensive rules
* **Handles errors gracefully** with automatic fallbacks
* **Provides detailed insights** for debugging and monitoring

Your First DataTidy Configuration
---------------------------------

Create a simple configuration file ``config.yaml``:

.. code-block:: yaml

   input:
     type: csv
     source: "data.csv"

   output:
     columns:
       user_id:
         source: "id"
         type: int
         validation:
           required: true

       clean_name:
         source: "name"
         transformation: "str(name).strip().title() if name else 'Unknown'"
         type: string

       age_category:
         transformation: "'adult' if age >= 18 else 'minor'"
         type: string
         validation:
           allowed_values: ["adult", "minor"]

Your First DataTidy Script
--------------------------

Create a simple Python script ``process_data.py``:

.. code-block:: python

   from datatidy import DataTidy

   # Initialize DataTidy
   dt = DataTidy('config.yaml')

   # Process data
   result = dt.process_data()

   # Display results
   print(result.head())

   # Save processed data
   dt.process_and_save('output.csv')

Command Line Usage
------------------

DataTidy includes a powerful CLI for batch processing:

.. code-block:: bash

   # Process data with configuration
   datatidy process config.yaml -i input.csv -o output.csv

   # Validate configuration
   datatidy validate config.yaml

   # Create sample configuration
   datatidy sample my_config.yaml

Enhanced Fallback Processing
----------------------------

For production environments, use the enhanced fallback system:

Create ``robust_config.yaml``:

.. code-block:: yaml

   input:
     type: csv
     source: "data.csv"

   output:
     columns:
       user_id:
         source: "id"
         type: int
         validation:
           required: true

       clean_name:
         source: "name"
         transformation: "str(name).strip().title() if name else 'Unknown'"
         type: string
         validation:
           required: true

       risk_score:
         transformation: "amount * risk_factor"
         type: float
         validation:
           min_value: 0
           max_value: 100

   global_settings:
     processing_mode: partial          # Enable partial processing
     enable_partial_processing: true
     enable_fallback: true
     max_column_failures: 5
     failure_threshold: 0.3            # 30% failure triggers fallback
     
     fallback_transformations:
       risk_score:
         type: default_value
         value: 50.0                   # Safe default

Production-Ready Script
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from datatidy import DataTidy
   import pandas as pd
   import logging

   def process_dashboard_data():
       """Production data processing with guaranteed results."""
       
       # Initialize with enhanced configuration
       dt = DataTidy('robust_config.yaml')
       
       # Define fallback database query
       def database_fallback():
           return pd.read_sql(
               "SELECT id as user_id, name, 50.0 as risk_score FROM users", 
               db_connection
           )
       
       try:
           # Process with fallback capabilities
           result = dt.process_data_with_fallback(
               fallback_query_func=database_fallback
           )
           
           # Check processing results
           summary = dt.get_processing_summary()
           logging.info(f"Processing completed: {summary}")
           
           # Handle different outcomes
           if result.fallback_used:
               logging.warning("Fallback processing used - check configuration")
           elif summary['failed_columns'] > 0:
               logging.warning(f"Partial processing: {summary['failed_columns']} columns failed")
           
           # Get recommendations for improvement
           recommendations = dt.get_processing_recommendations()
           if recommendations:
               logging.info("Processing recommendations:")
               for rec in recommendations:
                   logging.info(f"  - {rec}")
           
           # Always return data - never fail!
           return result.data
           
       except Exception as e:
           logging.error(f"Critical processing failure: {e}")
           # Emergency fallback
           return database_fallback()

   # Your dashboard always gets data
   dashboard_data = process_dashboard_data()

Enhanced CLI Usage
------------------

The enhanced CLI provides powerful debugging and monitoring capabilities:

.. code-block:: bash

   # Strict mode (default) - fails on any error
   datatidy process config.yaml --mode strict

   # Partial mode - skip problematic columns
   datatidy process config.yaml --mode partial --show-summary

   # Development mode with detailed feedback
   datatidy process config.yaml --mode partial \\
     --show-summary \\
     --show-recommendations \\
     --error-log debug.json

   # Fallback mode for maximum reliability
   datatidy process config.yaml --mode fallback

Example CLI Output
~~~~~~~~~~~~~~~~~

.. code-block:: text

   🔧 Loading configuration from: config.yaml
   🚀 Processing data in partial mode...
   💾 Processed data saved to: output.csv

   📈 Processing Summary:
      Mode: partial
      Success: ✅
      Processing time: 1.23s
      Successful columns: 8/10
      Failed columns: 2

   💡 Recommendations:
      🔍 Validation errors detected:
         - Check data types and null value handling
         - Consider using 'nullable: true' or providing default values

   ✅ Processing completed successfully!

Working with Different Data Sources
-----------------------------------

CSV Files
~~~~~~~~~

.. code-block:: yaml

   input:
     type: csv
     source: "data.csv"
     options:
       encoding: utf-8
       delimiter: ","
       header: 0

Excel Files
~~~~~~~~~~~

.. code-block:: yaml

   input:
     type: excel
     source: "data.xlsx"
     options:
       sheet_name: "Sheet1"
       header: 0
       skiprows: 2

Database Queries
~~~~~~~~~~~~~~~

.. code-block:: yaml

   input:
     type: database
     source:
       query: "SELECT * FROM users WHERE active = true"
       connection_string: "postgresql://user:pass@localhost/db"

Common Transformation Examples
------------------------------

String Cleaning
~~~~~~~~~~~~~~~

.. code-block:: yaml

   clean_name:
     source: "name"
     transformation: "str(name).strip().title() if name else 'Unknown'"
     type: string

Conditional Logic
~~~~~~~~~~~~~~~~

.. code-block:: yaml

   age_group:
     transformation: "'senior' if age > 65 else ('adult' if age >= 18 else 'minor')"
     type: string

Mathematical Calculations
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   bmi:
     transformation: "weight / (height / 100) ** 2"
     type: float
     validation:
       min_value: 10
       max_value: 50

Date Processing
~~~~~~~~~~~~~~

.. code-block:: yaml

   formatted_date:
     source: "created_at"
     type: datetime
     format: "%Y-%m-%d"

Error Handling and Debugging
----------------------------

Understanding Errors
~~~~~~~~~~~~~~~~~~~~

DataTidy categorizes errors for easier debugging:

* **Validation Errors**: Data doesn't meet validation rules
* **Transformation Errors**: Expression syntax or evaluation issues
* **Type Errors**: Data type conversion problems
* **Dependency Errors**: Missing referenced columns

Getting Error Details
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Check for processing errors
   if dt.has_errors():
       for error in dt.get_errors():
           print(f"Error: {error['message']}")

   # Get enhanced error report
   error_report = dt.get_error_report()
   print(error_report['error_summary'])

   # Export detailed error log
   dt.export_error_log("debug_errors.json")

Monitoring and Alerting
-----------------------

Production Monitoring
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Monitor processing health
   summary = dt.get_processing_summary()

   # Set up alerts
   if summary['failed_columns'] > 5:
       send_alert(f"High column failure rate: {summary['failed_columns']} columns failed")

   if summary['fallback_used']:
       send_alert("DataTidy fallback activated - investigate configuration")

Performance Monitoring
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Track performance metrics
   performance_metrics = {
       'processing_time': summary['processing_time'],
       'success_rate': summary['successful_columns'] / summary['total_columns'],
       'memory_usage': get_memory_usage()
   }

   # Send to monitoring system
   send_metrics_to_datadog(performance_metrics)

Best Practices
--------------

Configuration Management
~~~~~~~~~~~~~~~~~~~~~~~~

1. **Use version control** for configuration files
2. **Test configurations** with sample data first
3. **Use descriptive names** for transformations
4. **Document complex expressions** with comments

.. code-block:: yaml

   # Good: descriptive and documented
   revenue_risk_score:
     # Calculate risk based on revenue volatility and debt ratio
     transformation: "(revenue_std / revenue_mean) * debt_to_equity_ratio"
     type: float

Error Handling Strategy
~~~~~~~~~~~~~~~~~~~~~~

1. **Start with strict mode** during development
2. **Switch to partial mode** for production resilience
3. **Define fallback transformations** for critical columns
4. **Monitor processing health** with alerts

Development Workflow
~~~~~~~~~~~~~~~~~~~

1. **Create configuration** with sample data
2. **Test with strict mode** to identify all issues
3. **Add fallback transformations** for problematic columns
4. **Deploy with partial mode** for production reliability

Next Steps
----------

Now that you understand the basics, explore:

* :doc:`configuration` - Detailed configuration reference
* :doc:`fallback_system` - Advanced fallback system features
* :doc:`api/core` - Complete API documentation
* :doc:`examples` - More complex examples and use cases

Common Use Cases
---------------

Data Cleaning Pipeline
~~~~~~~~~~~~~~~~~~~~~

Perfect for cleaning messy datasets with consistent transformations:

.. code-block:: python

   # Clean customer data
   dt = DataTidy('customer_cleaning_config.yaml')
   clean_customers = dt.process_data('raw_customers.csv')

ETL Processing
~~~~~~~~~~~~~

Extract, transform, and load data with validation:

.. code-block:: python

   # ETL pipeline with validation
   dt = DataTidy('etl_config.yaml')
   result = dt.process_data_with_fallback()
   result.data.to_sql('processed_data', db_connection)

Dashboard Data Preparation
~~~~~~~~~~~~~~~~~~~~~~~~~

Prepare data for dashboards with guaranteed availability:

.. code-block:: python

   # Dashboard data that never fails to load
   dt = DataTidy('dashboard_config.yaml')
   dashboard_data = dt.process_data_with_fallback(
       fallback_query_func=lambda: get_basic_dashboard_data()
   )

Getting Help
------------

* **Documentation**: https://datatidy.readthedocs.io
* **GitHub Issues**: https://github.com/wwd1015/datatidy/issues
* **Examples**: See the ``examples/`` directory in the repository
* **Community**: GitHub Discussions for questions and tips