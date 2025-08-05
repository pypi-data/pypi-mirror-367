Configuration Module
===================

The configuration module handles parsing and validation of YAML configuration files.

ConfigParser Class
------------------

.. autoclass:: datatidy.config.parser.ConfigParser
   :members:
   :undoc-members:
   :show-inheritance:

   Parser for DataTidy YAML configuration files with validation and schema checking.

Schema Validation
-----------------

.. automodule:: datatidy.config.schema
   :members:
   :undoc-members:
   :show-inheritance:

Configuration Examples
----------------------

Basic Configuration
~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   input:
     type: csv
     source: "data/input.csv"
     options:
       encoding: utf-8
       delimiter: ","

   output:
     columns:
       user_id:
         source: "id"
         type: int
         validation:
           required: true
           min_value: 1
       
       full_name:
         source: "name"
         type: string
         transformation: "str.title()"
         validation:
           required: true
           min_length: 2
           max_length: 100

Enhanced Configuration with Fallbacks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   input:
     type: csv
     source: "data/input.csv"

   output:
     columns:
       facility_id:
         source: id
         type: int
         validation:
           required: true

       cash_flow_leverage:
         transformation: "debt_to_income * leverage_ratio"
         type: float
         validation:
           required: true
           min_value: 0
           max_value: 10

       risk_score:
         transformation: "np.where(cash_flow_leverage > 5, 'HIGH', 'LOW')"
         type: string
         validation:
           allowed_values: ["LOW", "MEDIUM", "HIGH"]

   global_settings:
     processing_mode: partial
     enable_partial_processing: true
     enable_fallback: true
     max_column_failures: 3
     failure_threshold: 0.4
     
     fallback_transformations:
       cash_flow_leverage:
         type: default_value
         value: 1.0
       
       risk_score:
         type: copy_column
         source: existing_risk_level

Configuration Schema
--------------------

Input Configuration
~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   input:
     type: csv | excel | database | parquet
     source: "file_path" | { query: "SQL", connection_string: "..." }
     options:
       # CSV options
       encoding: utf-8
       delimiter: ","
       header: 0
       
       # Excel options
       sheet_name: "Sheet1"
       header: 0
       skiprows: 0
       
       # Database options
       connection_string: "postgresql://..."

Output Configuration
~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   output:
     columns:
       column_name:
         source: "source_column"           # Optional: defaults to column_name
         type: int | float | string | bool | datetime
         transformation: "python_expression"
         default: "default_value"
         validation:
           required: true | false
           nullable: true | false
           min_value: number
           max_value: number
           min_length: number
           max_length: number
           pattern: "regex_pattern"
           allowed_values: [list, of, values]
         
         # Advanced operations
         operations:
           - type: map | filter | reduce
             expression: "lambda_expression"
             
     # Optional: filter and sort results
     filters:
       - condition: "expression"
         action: keep | remove
         
     sort:
       - column: "column_name"
         ascending: true | false

Global Settings
~~~~~~~~~~~~~~~

.. code-block:: yaml

   global_settings:
     # Error handling
     ignore_errors: false
     max_errors: 100
     
     # Enhanced fallback settings
     processing_mode: strict | partial | fallback
     enable_partial_processing: true
     enable_fallback: true
     max_column_failures: 5
     failure_threshold: 0.3
     
     # Debugging
     verbose: false
     show_execution_plan: false
     
     # Fallback transformations
     fallback_transformations:
       column_name:
         type: default_value | copy_column | basic_calculation
         value: "default_value"          # for default_value type
         source: "source_column"         # for copy_column type
         operation: mean | median | forward_fill  # for basic_calculation type

Validation Rules
----------------

DataTidy supports comprehensive validation rules:

Numeric Validations
~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   validation:
     required: true              # Field must not be null
     nullable: false             # Field cannot be null
     min_value: 0               # Minimum numeric value
     max_value: 100             # Maximum numeric value

String Validations
~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   validation:
     min_length: 2              # Minimum string length
     max_length: 50             # Maximum string length
     pattern: "^[A-Za-z]+$"     # Regex pattern
     allowed_values: ["A", "B"] # Whitelist of values

Usage Examples
--------------

Loading Configuration
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from datatidy.config.parser import ConfigParser

   # Parse from file
   parser = ConfigParser()
   config = parser.parse_file('config.yaml')

   # Parse from dictionary
   config_dict = {
       "input": {"type": "csv", "source": "data.csv"},
       "output": {"columns": {"id": {"source": "id", "type": "int"}}}
   }
   config = parser.parse_dict(config_dict)

   # Parse from YAML string
   yaml_string = '''
   input:
     type: csv
     source: data.csv
   output:
     columns:
       id:
         source: id
         type: int
   '''
   config = parser.parse_string(yaml_string)

Validation
~~~~~~~~~~

.. code-block:: python

   # Validate configuration
   try:
       parser.validate_config(config)
       print("Configuration is valid!")
   except ValueError as e:
       print(f"Configuration error: {e}")

Creating Sample Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Create a sample configuration
   sample_config = ConfigParser.create_sample_config()
   
   # Save to file
   import yaml
   with open('sample_config.yaml', 'w') as f:
       yaml.dump(sample_config, f, default_flow_style=False, indent=2)