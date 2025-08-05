Fallback System
===============

The fallback system provides robust error handling, partial processing capabilities, and enhanced logging for production environments.

Fallback Processor
------------------

.. autoclass:: datatidy.fallback.processor.FallbackProcessor
   :members:
   :undoc-members:
   :show-inheritance:

   Enhanced processor with fallback capabilities and partial processing.

Processing Result
-----------------

.. autoclass:: datatidy.fallback.processor.ProcessingResult
   :members:
   :undoc-members:
   :show-inheritance:

   Result of data processing with detailed information about success, failures, and fallback usage.

Enhanced Logger
---------------

.. autoclass:: datatidy.fallback.logger.EnhancedLogger
   :members:
   :undoc-members:
   :show-inheritance:

   Enhanced logger with detailed error categorization and metrics tracking.

Error Categories
~~~~~~~~~~~~~~~~

.. autoclass:: datatidy.fallback.logger.ErrorCategory
   :members:
   :undoc-members:
   :show-inheritance:

   Categories of errors for better debugging and analysis.

Processing Modes
~~~~~~~~~~~~~~~~

.. autoclass:: datatidy.fallback.logger.ProcessingMode
   :members:
   :undoc-members:
   :show-inheritance:

   Available processing modes for different reliability requirements.

Data Quality Metrics
---------------------

.. autoclass:: datatidy.fallback.metrics.DataQualityMetrics
   :members:
   :undoc-members:
   :show-inheritance:

   Utility class for comparing data quality between processing modes.

Quality Comparison
~~~~~~~~~~~~~~~~~~

.. autoclass:: datatidy.fallback.metrics.DataQualityComparison
   :members:
   :undoc-members:
   :show-inheritance:

   Complete comparison between DataTidy and fallback results.

Column Metrics
~~~~~~~~~~~~~~

.. autoclass:: datatidy.fallback.metrics.ColumnMetrics
   :members:
   :undoc-members:
   :show-inheritance:

   Metrics for a single column comparison.

Usage Examples
--------------

Basic Fallback Processing
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from datatidy.fallback.processor import FallbackProcessor
   from datatidy.fallback.logger import EnhancedLogger

   # Create logger and processor
   logger = EnhancedLogger()
   processor = FallbackProcessor(config, logger)

   # Process with fallback
   result = processor.process_with_fallback(data, transformation_engine)

   # Check results
   if result.success:
       print(f"✅ Processing successful: {len(result.successful_columns)} columns")
   else:
       print(f"⚠️ Processing issues: {len(result.failed_columns)} failed")

Error Categorization
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from datatidy.fallback.logger import EnhancedLogger, ErrorCategory

   logger = EnhancedLogger()

   # Log different types of errors
   logger.log_column_error(
       "amount", 
       ValueError("Required field has null values"), 
       ErrorCategory.VALIDATION_ERROR,
       indices=[1, 5, 10]
   )

   # Get debugging suggestions
   suggestions = logger.get_debugging_suggestions()
   for suggestion in suggestions:
       print(f"💡 {suggestion}")

Data Quality Comparison
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from datatidy.fallback.metrics import DataQualityMetrics

   # Compare processing results
   comparison = DataQualityMetrics.compare_results(
       datatidy_df=processed_data,
       fallback_df=fallback_data,
       datatidy_time=2.3,
       fallback_time=0.8
   )

   # Print detailed comparison
   DataQualityMetrics.print_comparison_summary(comparison)

   # Export for analysis
   DataQualityMetrics.export_comparison_report(
       comparison, 
       'quality_report.json'
   )

Configuration Examples
----------------------

Basic Fallback Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   global_settings:
     processing_mode: partial
     enable_partial_processing: true
     enable_fallback: true
     max_column_failures: 5
     failure_threshold: 0.3
     
     fallback_transformations:
       problematic_column:
         type: default_value
         value: "safe_default"

Advanced Fallback Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   global_settings:
     processing_mode: partial
     enable_partial_processing: true
     enable_fallback: true
     max_column_failures: 10
     failure_threshold: 0.4
     verbose: true
     show_execution_plan: true
     
     fallback_transformations:
       cash_flow_leverage:
         type: basic_calculation
         operation: mean
         source: debt_to_income
       
       risk_score:
         type: copy_column
         source: existing_risk_level
       
       formatted_id:
         type: default_value
         value: "UNKNOWN"

Error Handling Patterns
-----------------------

Production Error Handling
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def robust_data_processing(input_data, config_path):
       """Process data with comprehensive error handling."""
       
       dt = DataTidy(config_path)
       
       def database_fallback():
           return pd.read_sql("SELECT * FROM fallback_table", db_connection)
       
       try:
           # Try enhanced processing
           result = dt.process_data_with_fallback(
               input_data, 
               fallback_query_func=database_fallback
           )
           
           # Log processing metrics
           summary = dt.get_processing_summary()
           logger.info(f"Processing completed: {summary}")
           
           # Alert on issues
           if result.fallback_used:
               alert_team("DataTidy fallback activated")
           elif summary['failed_columns'] > 0:
               alert_team(f"Partial processing: {summary['failed_columns']} columns failed")
           
           # Always return data
           return result.data
           
       except Exception as e:
           logger.error(f"Critical processing failure: {e}")
           # Return basic fallback data
           return database_fallback()

Development Workflow
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def development_processing(data, config):
       """Development-friendly processing with detailed feedback."""
       
       dt = DataTidy()
       dt.config = config
       dt.set_processing_mode("partial")
       
       result = dt.process_data_with_fallback(data)
       
       if not result.success:
           print("🔍 Processing Issues Found:")
           
           # Show error details
           for error in result.error_log[:5]:
               print(f"   ❌ {error['column']}: {error['error_message']}")
           
           # Show recommendations
           recommendations = dt.get_processing_recommendations()
           print("\n💡 Recommendations:")
           for rec in recommendations:
               print(f"   {rec}")
           
           # Export detailed log
           dt.export_error_log("debug_errors.json")
           print("📁 Detailed error log saved to debug_errors.json")
       
       return result.data