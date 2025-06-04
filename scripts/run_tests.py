#!/usr/bin/env python
"""
Test runner script for LOTRO Forge.

Provides convenient commands for running different types of tests.
"""
import sys
import subprocess
import argparse
from pathlib import Path

def run_command(cmd: list[str], description: str) -> int:
    """Run a command and return the exit code."""
    print(f"\n🧪 {description}")
    print(f"Running: {' '.join(cmd)}")
    print("-" * 50)
    
    result = subprocess.run(cmd)
    return result.returncode

def main():
    parser = argparse.ArgumentParser(description="Run LOTRO Forge tests")
    parser.add_argument(
        "test_type",
        choices=["all", "unit", "integration", "api", "fast"],
        nargs="?",
        default="all",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Run tests with coverage reporting"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--file",
        "-f",
        help="Run specific test file"
    )
    
    args = parser.parse_args()
    
    # Base pytest command
    cmd = ["python", "-m", "pytest"]
    
    # Add coverage if requested
    if args.coverage:
        cmd.extend(["--cov=database", "--cov=web", "--cov=scripts", "--cov-report=html", "--cov-report=term"])
    
    # Add verbosity
    if args.verbose:
        cmd.append("-vv")
    
    # Add test selection
    if args.file:
        cmd.append(args.file)
    elif args.test_type == "unit":
        cmd.extend(["-m", "unit", "tests/unit/"])
    elif args.test_type == "integration":
        cmd.extend(["-m", "integration", "tests/integration/"])
    elif args.test_type == "api":
        cmd.extend(["-m", "api", "tests/integration/test_api.py"])
    elif args.test_type == "fast":
        cmd.extend(["-m", "not slow"])
    else:  # all
        cmd.append("tests/")
    
    # Run the tests
    description = f"Running {args.test_type} tests"
    if args.coverage:
        description += " with coverage"
    
    exit_code = run_command(cmd, description)
    
    if exit_code == 0:
        print("\n✅ All tests passed!")
        if args.coverage:
            print("📊 Coverage report generated in htmlcov/")
    else:
        print(f"\n❌ Tests failed with exit code {exit_code}")
    
    return exit_code

if __name__ == "__main__":
    sys.exit(main()) 