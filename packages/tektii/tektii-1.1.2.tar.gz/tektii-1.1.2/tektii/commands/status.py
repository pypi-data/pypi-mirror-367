"""Status command implementation for environment health checks."""

import os
import subprocess
import sys
from pathlib import Path
from typing import Any, List, Tuple

from ..utils.colors import Colors, print_colored, print_header


def check_python_version() -> Tuple[bool, str]:
    """Check if Python version meets requirements."""
    version = sys.version_info
    min_version = (3, 8)

    if version >= min_version:
        return True, f"Python {version.major}.{version.minor}.{version.micro}"
    else:
        return False, f"Python {version.major}.{version.minor}.{version.micro} (requires >= 3.8)"


def check_tektii_installation() -> Tuple[bool, str]:
    """Check if tektii package is properly installed."""
    try:
        import tektii

        version = getattr(tektii, "__version__", "unknown")
        return True, f"tektii {version}"
    except ImportError:
        return False, "tektii package not installed"


def check_protobuf() -> Tuple[bool, str]:
    """Check if protobuf files are generated."""
    proto_dir = Path(__file__).parent.parent / "strategy" / "grpc"
    pb2_files = list(proto_dir.glob("*_pb2.py"))

    if pb2_files:
        return True, f"{len(pb2_files)} protobuf files found"
    else:
        return False, "No protobuf files found (run 'make proto')"


def check_docker() -> Tuple[bool, str]:
    """Check if Docker is available."""
    try:
        result = subprocess.run(["docker", "--version"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version = result.stdout.strip()
            return True, version
        else:
            return False, "Docker not found"
    except (subprocess.SubprocessError, FileNotFoundError):
        return False, "Docker not available"


def check_api_config() -> Tuple[bool, str]:
    """Check if API configuration exists."""
    config_path = Path.home() / ".tektii" / "config.json"

    if config_path.exists():
        return True, f"Config found at {config_path}"
    else:
        return False, "No API configuration (run 'tektii push --save-config')"


def check_example_strategy() -> Tuple[bool, str]:
    """Check if example strategies exist."""
    examples_dir = Path("examples")

    if examples_dir.exists():
        strategies = list(examples_dir.glob("*.py"))
        if strategies:
            return True, f"{len(strategies)} example strategies found"

    return False, "No example strategies found"


def get_recent_strategies() -> List[str]:
    """Get list of recently modified strategy files."""
    strategies = []
    for pattern in ["*.py", "strategies/*.py"]:
        for file in Path(".").glob(pattern):
            if file.stem.startswith("test_"):
                continue
            if any(keyword in file.read_text() for keyword in ["TektiiStrategy", "class"]):
                strategies.append(str(file))

    # Sort by modification time, most recent first
    strategies.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    return strategies[:5]  # Return top 5


def cmd_status(args: Any) -> int:
    """Show current environment status and health checks."""
    print_header("Tektii SDK Status")

    # Run health checks
    checks = [
        ("Python Version", check_python_version),
        ("Tektii Installation", check_tektii_installation),
        ("Protobuf Files", check_protobuf),
        ("Docker", check_docker),
        ("API Configuration", check_api_config),
        ("Example Strategies", check_example_strategy),
    ]

    all_passed = True
    results = []

    print_colored("\nEnvironment Checks:", Colors.HEADER)
    for name, check_func in checks:
        passed, message = check_func()
        all_passed = all_passed and passed

        status = "✓" if passed else "✗"
        color = Colors.OKGREEN if passed else Colors.FAIL
        print_colored(f"  {status} {name}: {message}", color)

        results.append((name, passed, message))

    # Show recent strategies
    print_colored("\nRecent Strategies:", Colors.HEADER)
    strategies = get_recent_strategies()
    if strategies:
        for strategy in strategies:
            print(f"  • {strategy}")
    else:
        print_colored("  No strategies found in current directory", Colors.WARNING)

    # Show next steps if detailed
    if args.detailed or not all_passed:
        print_colored("\nNext Steps:", Colors.HEADER)

        for name, _, _ in results:
            if not passed:
                if "Python" in name:
                    print("  • Upgrade Python: pyenv install 3.11 && pyenv local 3.11")
                elif "Installation" in name:
                    print("  • Install package: pip install -e .")
                elif "Protobuf" in name:
                    print("  • Generate protobuf: make proto")
                elif "Docker" in name:
                    print("  • Install Docker: https://docs.docker.com/get-docker/")
                elif "API Configuration" in name:
                    print("  • Configure API: tektii push <strategy> --save-config")
                elif "Example" in name:
                    print("  • Create example: tektii new my_first_strategy --with-tests")

    # Quick start guide
    if not strategies and all_passed:
        print_colored("\nQuick Start:", Colors.OKCYAN)
        print("  1. Create a strategy: tektii new my_strategy")
        print("  2. Validate it: tektii validate my_strategy.py")
        print("  3. Run locally: tektii serve my_strategy.py MyStrategy")
        print("  4. Deploy: tektii push my_strategy.py MyStrategy")

    return 0 if all_passed else 1
