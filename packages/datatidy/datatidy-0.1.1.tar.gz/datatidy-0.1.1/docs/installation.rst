Installation
============

DataTidy can be installed using pip from PyPI or from source for development.

Requirements
------------

* Python 3.8 or higher
* pandas >= 1.5.0
* PyYAML >= 6.0
* Other dependencies are automatically installed

Basic Installation
------------------

Install DataTidy from PyPI:

.. code-block:: bash

   pip install datatidy

This will install DataTidy with all core dependencies needed for basic functionality.

Development Installation
------------------------

For development or to get the latest features:

.. code-block:: bash

   git clone https://github.com/wwd1015/datatidy.git
   cd datatidy
   pip install -e ".[dev]"

This installs DataTidy in "editable" mode with development dependencies including:

* pytest for testing
* black for code formatting
* flake8 for linting
* mypy for type checking

Optional Dependencies
--------------------

DataTidy supports optional dependencies for extended functionality:

.. code-block:: bash

   # For enhanced Parquet support
   pip install "datatidy[all]"

   # Or install specific extras
   pip install pyarrow  # For Parquet files
   pip install fastparquet  # Alternative Parquet engine

Database Dependencies
~~~~~~~~~~~~~~~~~~~~

For database connectivity, install the appropriate database drivers:

.. code-block:: bash

   # PostgreSQL
   pip install psycopg2-binary

   # MySQL
   pip install pymysql

   # Snowflake
   pip install snowflake-sqlalchemy

   # All database drivers
   pip install psycopg2-binary pymysql snowflake-sqlalchemy

Verification
------------

Verify your installation:

.. code-block:: python

   import datatidy
   print(datatidy.__version__)

   # Test basic functionality
   from datatidy import DataTidy
   dt = DataTidy()
   print("✅ DataTidy installed successfully!")

Test Enhanced Features
~~~~~~~~~~~~~~~~~~~~~

Test the enhanced fallback system:

.. code-block:: python

   from datatidy import DataTidy, ProcessingMode
   from datatidy.fallback import EnhancedLogger, DataQualityMetrics

   # Test fallback imports
   dt = DataTidy()
   logger = EnhancedLogger()
   
   print("✅ Enhanced fallback system available!")

Docker Installation
-------------------

DataTidy can be used in Docker containers:

.. code-block:: dockerfile

   FROM python:3.9-slim

   # Install system dependencies
   RUN apt-get update && apt-get install -y \\
       gcc \\
       && rm -rf /var/lib/apt/lists/*

   # Install DataTidy
   RUN pip install datatidy

   # Copy your configuration and scripts
   COPY config.yaml /app/
   COPY process_data.py /app/

   WORKDIR /app
   CMD ["python", "process_data.py"]

Upgrading
---------

To upgrade DataTidy to the latest version:

.. code-block:: bash

   pip install --upgrade datatidy

To upgrade to a pre-release version:

.. code-block:: bash

   pip install --upgrade --pre datatidy

Common Issues
-------------

Import Errors
~~~~~~~~~~~~~

If you encounter import errors, ensure all dependencies are installed:

.. code-block:: bash

   pip install --upgrade pandas pyyaml sqlalchemy openpyxl

Permission Errors
~~~~~~~~~~~~~~~~

If you encounter permission errors during installation:

.. code-block:: bash

   # Use user installation
   pip install --user datatidy

   # Or use virtual environment (recommended)
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   pip install datatidy

Virtual Environment Setup
-------------------------

It's recommended to use a virtual environment:

.. code-block:: bash

   # Create virtual environment
   python -m venv datatidy-env

   # Activate virtual environment
   # On macOS/Linux:
   source datatidy-env/bin/activate
   # On Windows:
   datatidy-env\\Scripts\\activate

   # Install DataTidy
   pip install datatidy

   # Deactivate when done
   deactivate

Conda Installation
------------------

While DataTidy is not yet available on conda-forge, you can install it in a conda environment:

.. code-block:: bash

   # Create conda environment
   conda create -n datatidy python=3.9
   conda activate datatidy

   # Install DataTidy with pip
   pip install datatidy

System Requirements
-------------------

Minimum Requirements
~~~~~~~~~~~~~~~~~~~

* **CPU**: Any modern processor
* **Memory**: 512 MB RAM (for small datasets < 10K rows)
* **Storage**: 50 MB for installation

Recommended Requirements
~~~~~~~~~~~~~~~~~~~~~~~

* **CPU**: Multi-core processor
* **Memory**: 2+ GB RAM (for datasets > 100K rows)
* **Storage**: 100 MB+ for logging and temporary files

Performance Scaling
~~~~~~~~~~~~~~~~~~~

DataTidy performance scales with:

* **Memory**: More RAM allows processing larger datasets
* **CPU**: Multi-core processors improve expression evaluation
* **Storage**: SSD storage improves I/O performance for large files

Platform Support
----------------

DataTidy is tested on:

* **macOS**: 10.15+
* **Linux**: Ubuntu 18.04+, CentOS 7+, Amazon Linux 2
* **Windows**: Windows 10+

Architecture Support
~~~~~~~~~~~~~~~~~~~

* **x86_64**: Full support
* **ARM64**: Full support (including Apple Silicon Macs)
* **Other architectures**: Should work but not regularly tested

Troubleshooting
---------------

Installation Fails
~~~~~~~~~~~~~~~~~~

If installation fails, try:

.. code-block:: bash

   # Update pip first
   pip install --upgrade pip

   # Clear pip cache
   pip cache purge

   # Try with verbose output
   pip install -v datatidy

Memory Issues
~~~~~~~~~~~~~

For large datasets, ensure adequate memory:

.. code-block:: python

   import pandas as pd
   
   # Check available memory
   import psutil
   print(f"Available memory: {psutil.virtual_memory().available / 1024**3:.1f} GB")
   
   # For large files, consider chunking
   for chunk in pd.read_csv('large_file.csv', chunksize=10000):
       # Process chunk with DataTidy
       pass

Getting Help
------------

If you encounter issues:

1. **Check the documentation**: https://datatidy.readthedocs.io
2. **Search existing issues**: https://github.com/wwd1015/datatidy/issues
3. **Create a new issue**: Include your Python version, OS, and error message
4. **Community support**: Ask questions in GitHub Discussions

Next Steps
----------

After installation, see:

* :doc:`quickstart` - Get started with basic usage
* :doc:`configuration` - Learn about configuration options
* :doc:`fallback_system` - Understand the enhanced fallback system
* :doc:`examples` - See practical examples