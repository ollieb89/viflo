#!/usr/bin/env python3
"""
Test runner for GSD workflow scripts.
Run with: python3 run_tests.py
"""

import sys
import subprocess
from pathlib import Path


def check_pytest_cov():
    """Check if pytest-cov is installed."""
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "--version"],
        capture_output=True,
        text=True
    )
    return "pytest-cov" in result.stdout or "cov" in result.stdout


def run_tests():
    """Run all tests with optional coverage report."""
    test_dir = Path(__file__).parent
    
    # Add scripts directory to path
    scripts_dir = test_dir.parent / "scripts"
    sys.path.insert(0, str(scripts_dir))
    
    use_cov = "--cov" in sys.argv
    
    # Build command
    cmd = [
        sys.executable, "-m", "pytest",
        str(test_dir),
        "-v",
        "--tb=short",
    ]
    
    # Add coverage only if requested and available
    if use_cov:
        if check_pytest_cov():
            cmd.extend(["--cov=scripts", "--cov-report=term-missing"])
        else:
            print("⚠️  pytest-cov not installed. Running without coverage.")
            print("   Install with: pip install pytest-cov")
            print()
    
    print("=" * 70)
    print("Running GSD Workflow Tests")
    print("=" * 70)
    print()
    
    result = subprocess.run(cmd)
    return result.returncode


def run_specific_test(test_file):
    """Run a specific test file."""
    test_dir = Path(__file__).parent
    scripts_dir = test_dir.parent / "scripts"
    sys.path.insert(0, str(scripts_dir))
    
    cmd = [
        sys.executable, "-m", "pytest",
        str(test_dir / test_file),
        "-v",
        "--tb=short"
    ]
    
    print(f"Running {test_file}...")
    result = subprocess.run(cmd)
    return result.returncode


if __name__ == "__main__":
    if len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
        # Run specific test file
        sys.exit(run_specific_test(sys.argv[1]))
    else:
        sys.exit(run_tests())
