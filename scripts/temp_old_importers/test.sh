#!/bin/bash

# Exit on any error
set -e

# Print commands as they are executed
set -x

# Ensure we're in the project root directory
cd "$(dirname "$0")/.."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Error: virtual environment not found. Please run 'python -m venv venv' first."
    exit 1
fi

# Run all tests in the tests/unit directory with verbose output
python -m unittest discover -s tests/unit -p "test_*.py" 