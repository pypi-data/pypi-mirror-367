"""
Pytest configuration file.

This file is automatically loaded by pytest and can be used to configure the test environment.
"""

import os
import sys

# Add the project root directory to the Python path
# This allows the test files to import the modules from the package
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))