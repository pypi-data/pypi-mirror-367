Core Module
===========

The core module contains the main DataTidy class for orchestrating data processing.

DataTidy Class
--------------

.. autoclass:: datatidy.DataTidy
   :members:
   :undoc-members:
   :show-inheritance:

   The main class for configuration-driven data processing with enhanced fallback capabilities.

   .. note::
      The DataTidy class provides both traditional processing methods and enhanced
      fallback processing for production environments requiring 100% reliability.

Core Methods
~~~~~~~~~~~~

.. automethod:: datatidy.DataTidy.load_config
.. automethod:: datatidy.DataTidy.process_data
.. automethod:: datatidy.DataTidy.process_and_save

Enhanced Fallback Methods
~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: datatidy.DataTidy.process_data_with_fallback
.. automethod:: datatidy.DataTidy.get_processing_summary
.. automethod:: datatidy.DataTidy.get_error_report
.. automethod:: datatidy.DataTidy.get_processing_recommendations
.. automethod:: datatidy.DataTidy.compare_with_fallback
.. automethod:: datatidy.DataTidy.export_error_log
.. automethod:: datatidy.DataTidy.set_processing_mode

Example Usage
~~~~~~~~~~~~~

Basic Processing
^^^^^^^^^^^^^^^^

.. code-block:: python

   from datatidy import DataTidy

   # Initialize with configuration file
   dt = DataTidy('config.yaml')

   # Process data
   result_df = dt.process_data('input.csv')

   # Save result
   dt.process_and_save('output.csv', 'input.csv')

Enhanced Processing with Fallback
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from datatidy import DataTidy
   import pandas as pd

   # Initialize DataTidy
   dt = DataTidy('config.yaml')

   # Define fallback database query
   def fallback_database_query():
       return pd.read_sql("SELECT * FROM facilities", db_connection)

   # Process with guaranteed results
   result = dt.process_data_with_fallback(
       data=input_df,
       fallback_query_func=fallback_database_query
   )

   # Your application always gets data!
   if result.fallback_used:
       logger.warning("DataTidy processing failed, using database fallback")

   # Check processing results
   summary = dt.get_processing_summary()
   print(f"Success: {summary['success']}")
   print(f"Successful columns: {summary['successful_columns']}")

Production Monitoring
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   # Get improvement recommendations
   recommendations = dt.get_processing_recommendations()
   for rec in recommendations:
       print(f"💡 {rec}")

   # Export detailed error log
   dt.export_error_log("processing_errors.json")

   # Compare data quality when both available
   if not result.fallback_used:
       fallback_data = fallback_database_query()
       quality = dt.compare_with_fallback(fallback_data)
       print(f"Overall quality score: {quality.overall_quality_score:.2f}")

Processing Modes
~~~~~~~~~~~~~~~~

DataTidy supports three processing modes for different reliability requirements:

**Strict Mode** (Default)
  Fails completely if any column fails. Best for critical data processing where accuracy is paramount.

**Partial Mode** (Recommended for Development)
  Processes successful columns, skips failed ones. Shows detailed error information for debugging.

**Fallback Mode** (Production Resilience)
  Uses fallback transformations when primary processing fails. Ensures data is always returned.

.. code-block:: python

   # Set processing mode
   dt.set_processing_mode("partial")

   # Or configure in YAML
   global_settings:
     processing_mode: partial
     enable_partial_processing: true
     enable_fallback: true