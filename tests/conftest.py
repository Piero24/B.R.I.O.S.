"""Pytest configuration file to set up the test environment."""

import sys
from pathlib import Path

# Add the project root directory to the Python path
# This allows importing the main module from tests
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
