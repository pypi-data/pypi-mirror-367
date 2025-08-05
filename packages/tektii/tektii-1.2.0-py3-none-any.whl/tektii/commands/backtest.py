"""Backtest command implementation for running historical strategy tests on Tektii platform."""

import json
import os
import time
from datetime import datetime
from typing import Any, Dict, Optional, cast

import requests

from ..utils.colors import Colors, print_colored, print_header


class TektiiBacktester:
    """Backtest client for Tektii platform."""

    def __init__(self, api_url: str = "https://api.tektii.com"):
        """Initialize backtest client."""
        self.api_url = api_url
        self.session = requests.Session()
        self._load_config()

    def _load_config(self) -> None:
        """Load API configuration."""
        from pathlib import Path

        config_path = Path.home() / ".tektii" / "config.json"

        if config_path.exists():
            with open(config_path) as f:
                config = json.load(f)
                self.api_key = config.get("api_key", "")
                self.api_url = config.get("api_url", self.api_url)
                if self.api_key:
                    self.session.headers["Authorization"] = f"Bearer {self.api_key}"
        else:
            self.api_key = None

    def trigger_backtest(
        self,
        strategy_id: str,
        start_date: str,
        end_date: str,
        symbols: list[str],
        initial_capital: float = 100000,
        commission: float = 0.001,
        slippage: float = 0.0001,
    ) -> Dict[str, Any]:
        """Trigger a backtest on the Tektii platform."""
        if not self.api_key:
            return {"error": "No API key configured. Run 'tektii push --save-config' first"}

        # Prepare backtest request
        backtest_config = {
            "strategy_id": strategy_id,
            "start_date": start_date,
            "end_date": end_date,
            "symbols": symbols,
            "initial_capital": initial_capital,
            "commission": commission,
            "slippage": slippage,
        }

        print_colored("Submitting backtest request to Tektii platform...", Colors.OKCYAN)

        try:
            # Submit backtest request
            response = self.session.post(f"{self.api_url}/v1/backtests", json=backtest_config, timeout=30)

            if response.status_code == 401:
                return {"error": "Authentication failed. Check your API key"}
            elif response.status_code != 200:
                return {"error": f"API error: {response.status_code} - {response.text}"}

            result = response.json()
            return cast(Dict[str, Any], result)

        except requests.exceptions.ConnectionError:
            return {"error": "Could not connect to Tektii API. Check your internet connection"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    def get_backtest_status(self, backtest_id: str) -> Dict[str, Any]:
        """Check the status of a running backtest."""
        if not self.api_key:
            return {"error": "No API key configured"}

        try:
            response = self.session.get(f"{self.api_url}/v1/backtests/{backtest_id}/status", timeout=10)

            if response.status_code == 200:
                return cast(Dict[str, Any], response.json())
            else:
                return {"error": f"Failed to get status: {response.status_code}"}

        except Exception as e:
            return {"error": f"Error checking status: {str(e)}"}

    def get_backtest_results(self, backtest_id: str) -> Dict[str, Any]:
        """Retrieve results of a completed backtest."""
        if not self.api_key:
            return {"error": "No API key configured"}

        try:
            response = self.session.get(f"{self.api_url}/v1/backtests/{backtest_id}/results", timeout=30)

            if response.status_code == 200:
                return cast(Dict[str, Any], response.json())
            elif response.status_code == 404:
                return {"error": "Backtest not found or not yet complete"}
            else:
                return {"error": f"Failed to get results: {response.status_code}"}

        except Exception as e:
            return {"error": f"Error retrieving results: {str(e)}"}

    def wait_for_completion(self, backtest_id: str, timeout: int = 300, poll_interval: int = 5) -> Optional[Dict[str, Any]]:
        """Wait for backtest to complete with polling."""
        start_time = time.time()

        while time.time() - start_time < timeout:
            status = self.get_backtest_status(backtest_id)

            if "error" in status:
                return status

            state = status.get("state", "unknown")
            progress = status.get("progress", 0)

            if state == "completed":
                print_colored("\n✓ Backtest completed!", Colors.OKGREEN)
                return self.get_backtest_results(backtest_id)
            elif state == "failed":
                error_msg = status.get("error", "Unknown error")
                print_colored(f"\n✗ Backtest failed: {error_msg}", Colors.FAIL)
                return {"error": error_msg}
            else:
                # Show progress
                print(f"\rBacktest progress: {progress}% [{state}]", end="", flush=True)
                time.sleep(poll_interval)

        return {"error": "Backtest timed out"}


def create_local_demo_results(start_date: str, end_date: str, symbols: list[str]) -> Dict[str, Any]:
    """Create demo results for local testing (temporary until API is ready)."""
    # This is a placeholder that creates sample results
    # In production, this would come from the actual Tektii platform

    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    days = (end - start).days

    # Generate sample equity curve
    equity_curve = []
    current_value = 100000.0
    for i in range(days):
        # Simulate some growth with volatility
        import random

        daily_return = random.gauss(0.0003, 0.02)  # 0.03% daily return with 2% volatility
        current_value = float(current_value * (1 + daily_return))
        equity_curve.append({"date": (start.timestamp() + i * 86400) * 1000, "value": current_value})

    # Calculate metrics
    total_return = (current_value - 100000) / 100000

    return {
        "backtest_id": "demo_" + str(int(time.time())),
        "status": "completed",
        "summary": {
            "initial_capital": 100000,
            "final_value": current_value,
            "total_return": total_return,
            "total_return_pct": total_return * 100,
            "max_drawdown": 0.15,  # 15% drawdown
            "max_drawdown_pct": 15,
            "num_trades": 42,
            "win_rate": 0.58,
            "commission_paid": 210.50,
        },
        "period": {"start": start_date, "end": end_date, "days": days},
        "equity_curve": equity_curve,
        "trades": [],  # Would include detailed trades in real implementation
    }


def cmd_backtest(args: Any) -> int:
    """Run strategy backtest on the Tektii platform."""
    module_path = args.module
    class_name = args.class_name

    if not os.path.exists(module_path):
        print_colored(f"Error: {module_path} not found", Colors.FAIL)
        return 1

    print_header(f"Backtesting {class_name}")

    # Parse symbols
    symbols = args.symbols.split(",") if args.symbols else ["AAPL", "GOOGL"]

    # Create backtest client
    client = TektiiBacktester()

    # Check if we have API configuration
    if not client.api_key:
        print_colored("\nNote: No API configuration found. Using local demo mode.", Colors.WARNING)
        print_colored("To use the Tektii platform, run: tektii push --save-config\n", Colors.OKCYAN)

        # Create demo results for testing
        results = create_local_demo_results(start_date=args.start, end_date=args.end, symbols=symbols)
    else:
        # Get strategy ID from config or use a placeholder
        # In a real implementation, this would be retrieved from the push command
        strategy_id = "strategy_" + class_name.lower()

        # Trigger backtest on platform
        response = client.trigger_backtest(
            strategy_id=strategy_id,
            start_date=args.start,
            end_date=args.end,
            symbols=symbols,
            initial_capital=args.initial_capital,
            commission=args.commission,
            slippage=args.slippage,
        )

        if "error" in response:
            print_colored(f"\nError: {response['error']}", Colors.FAIL)
            return 1

        backtest_id = response.get("backtest_id")
        if not backtest_id:
            print_colored("\nError: No backtest ID returned", Colors.FAIL)
            return 1

        print_colored(f"\nBacktest ID: {backtest_id}", Colors.OKCYAN)
        print_colored("Waiting for backtest to complete...", Colors.OKCYAN)

        # Wait for completion
        backtest_results: Optional[Dict[str, Any]] = client.wait_for_completion(backtest_id)

        if not backtest_results or "error" in backtest_results:
            error_msg = backtest_results.get("error", "Unknown error") if backtest_results else "Timeout"
            print_colored(f"\nBacktest failed: {error_msg}", Colors.FAIL)
            return 1

        results = backtest_results

    # Display summary
    summary = results.get("summary", {})
    print_colored("\nBacktest Results:", Colors.HEADER)
    print(f"  Initial Capital:  ${summary.get('initial_capital', 0):,.2f}")
    print(f"  Final Value:      ${summary.get('final_value', 0):,.2f}")
    print(f"  Total Return:     {summary.get('total_return_pct', 0):.2f}%")
    print(f"  Max Drawdown:     {summary.get('max_drawdown_pct', 0):.2f}%")
    print(f"  Number of Trades: {summary.get('num_trades', 0)}")
    print(f"  Win Rate:         {summary.get('win_rate', 0):.1%}")
    print(f"  Commission Paid:  ${summary.get('commission_paid', 0):,.2f}")

    # Save results locally
    output_file = args.output or "backtest_results.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print_colored(f"\n✓ Results saved to {output_file}", Colors.OKGREEN)
    print_colored(f"Run 'tektii analyze {output_file}' for detailed analysis", Colors.OKCYAN)

    # If this was a platform backtest, provide the ID for future reference
    if client.api_key and "backtest_id" in results:
        print_colored(f"\nPlatform backtest ID: {results['backtest_id']}", Colors.OKCYAN)
        print_colored("You can retrieve these results anytime with:", Colors.OKCYAN)
        print(f"  tektii analyze --backtest-id {results['backtest_id']}")

    return 0
