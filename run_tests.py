#!/usr/bin/env python3
"""
Simple test runner for LOTRO Forge.

Runs all tests in the tests/ directory using pytest.
"""
import sys
import subprocess
from pathlib import Path

def main():
    """Run all tests using pytest."""
    print("🧪 Running LOTRO Forge tests...")
    print("=" * 40)
    
    # Check if pytest is available
    try:
        import pytest
    except ImportError:
        print("❌ pytest not found. Please install it with: pip install pytest")
        return 1
    
    # Run tests
    cmd = [sys.executable, "-m", "pytest", "tests/", "-v"]
    
    print(f"Running: {' '.join(cmd)}")
    print("-" * 40)
    
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ Tests failed with exit code {result.returncode}")
    
    return result.returncode

if __name__ == "__main__":
    sys.exit(main()) 