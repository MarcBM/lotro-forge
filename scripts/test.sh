#!/bin/bash

# Exit on any error
set -e

# Print commands as they are executed
set -x

# Run all tests in the tests directory
python -m unittest discover -s tests -p "test_*.py" 