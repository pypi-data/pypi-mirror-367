"""Test command implementation for running strategy tests."""

import os
import subprocess
import sys
from typing import Any

from ..utils.colors import Colors, print_colored, print_header


def cmd_test(args: Any) -> int:
    """Run strategy tests."""
    test_file = args.file

    if not os.path.exists(test_file):
        # Try to find test file
        if os.path.exists(f"test_{test_file}"):
            test_file = f"test_{test_file}"
        elif os.path.exists(test_file.replace(".py", "_test.py")):
            test_file = test_file.replace(".py", "_test.py")
        else:
            print_colored("Error: Test file not found", Colors.FAIL)
            return 1

    print_header(f"Running tests from {test_file}")

    # Run tests using pytest or unittest
    try:
        import pytest

        exit_code = pytest.main([test_file, "-v"])
    except ImportError:
        # Fall back to unittest
        result = subprocess.run([sys.executable, "-m", "unittest", test_file, "-v"])
        exit_code = result.returncode

    if exit_code == 0:
        print()
        print_colored("✓ All tests passed!", Colors.OKGREEN + Colors.BOLD)
    else:
        print()
        print_colored("✗ Some tests failed", Colors.FAIL)

    return int(exit_code)
