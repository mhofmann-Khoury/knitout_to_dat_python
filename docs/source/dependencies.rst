Dependencies
============

Complete overview of dependencies and version requirements.

🐍 Python Version Requirements
------------------------------

KnitScript requires **Python 3.11 or 3.12**.

**Supported Python Versions:**

.. list-table::
   :widths: 20 20 60
   :header-rows: 1

   * - 3.11
     - ✅ Supported
     - Improved performance
   * - 3.12
     - ✅ Supported
     - Latest features and optimizations

📦 Runtime Dependencies
-----------------------

Core Dependencies
~~~~~~~~~~~~~~~~~

These packages are automatically installed:

**virtual-knitting-machine** (^0.0.13)
   Virtual machine simulation for knitting operations.

   - Simulates V-bed knitting machine behavior
   - Tracks machine state during pattern execution
   - Validates machine operations and constraints

**knitout-interpreter** (^0.0.18)
   Knitout processing and execution framework.

   - Processes generated knitout instructions
   - Provides instruction validation and optimization
   - Handles knitout format compliance

For more information about the broader knitting software ecosystem, see :doc:`related_projects`.
