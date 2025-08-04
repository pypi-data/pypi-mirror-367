"""Analyze command implementation for performance analysis of backtest results."""

import json
import math
import os
from typing import Any, Dict, List, Optional, cast

import requests

from ..utils.colors import Colors, print_colored, print_header


class PerformanceAnalyzer:
    """Analyze backtest results and calculate performance metrics."""

    def __init__(self, results: Dict[str, Any]):
        """Initialize analyzer with backtest results."""
        self.results = results
        self.trades = results.get("trades", [])
        self.equity_curve = results.get("equity_curve", [])
        self.summary = results.get("summary", {})

    def calculate_sharpe_ratio(self, risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio."""
        if len(self.equity_curve) < 2:
            return 0.0

        # Calculate daily returns
        returns = []
        for i in range(1, len(self.equity_curve)):
            prev_value = self.equity_curve[i - 1]["value"]
            curr_value = self.equity_curve[i]["value"]
            if prev_value > 0:
                daily_return = (curr_value - prev_value) / prev_value
                returns.append(daily_return)

        if not returns:
            return 0.0

        # Calculate mean and std dev
        mean_return = sum(returns) / len(returns)
        variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
        std_dev = math.sqrt(variance)

        if std_dev == 0:
            return 0.0

        # Annualize (assuming 252 trading days)
        annual_return = mean_return * 252
        annual_std = std_dev * math.sqrt(252)

        return float((annual_return - risk_free_rate) / annual_std) if annual_std > 0 else 0.0

    def calculate_sortino_ratio(self, risk_free_rate: float = 0.02) -> float:
        """Calculate Sortino ratio (uses downside deviation)."""
        if len(self.equity_curve) < 2:
            return 0.0

        # Calculate daily returns
        returns = []
        for i in range(1, len(self.equity_curve)):
            prev_value = self.equity_curve[i - 1]["value"]
            curr_value = self.equity_curve[i]["value"]
            if prev_value > 0:
                daily_return = (curr_value - prev_value) / prev_value
                returns.append(daily_return)

        if not returns:
            return 0.0

        # Calculate mean return
        mean_return = sum(returns) / len(returns)

        # Calculate downside deviation (only negative returns)
        negative_returns = [r for r in returns if r < 0]
        if not negative_returns:
            return float("inf")  # No downside risk

        downside_variance = sum(r**2 for r in negative_returns) / len(returns)
        downside_deviation = math.sqrt(downside_variance)

        if downside_deviation == 0:
            return float("inf")

        # Annualize
        annual_return = mean_return * 252
        annual_downside_dev = downside_deviation * math.sqrt(252)

        return float((annual_return - risk_free_rate) / annual_downside_dev) if annual_downside_dev > 0 else 0.0

    def calculate_calmar_ratio(self) -> float:
        """Calculate Calmar ratio (annual return / max drawdown)."""
        max_dd = self.summary.get("max_drawdown", 0)
        if max_dd == 0:
            return float("inf")

        # Calculate annualized return
        period_days = self.results.get("period", {}).get("days", 365)
        total_return = self.summary.get("total_return", 0)

        if period_days > 0:
            annual_return = (1 + total_return) ** (365 / period_days) - 1
            return float(annual_return / max_dd)

        return 0.0

    def analyze_trades(self) -> Dict[str, Any]:
        """Analyze trade statistics."""
        if not self.trades:
            return {}

        # Separate buys and sells
        buys = [t for t in self.trades if t["side"] == "BUY"]
        sells = [t for t in self.trades if t["side"] == "SELL"]

        # Calculate trade statistics
        avg_trade_size = sum(t["value"] for t in self.trades) / len(self.trades) if self.trades else 0

        # Win/loss analysis (simplified - pairs buys with next sell)
        profits: List[float] = []
        position_map: Dict[str, List[Dict[str, Any]]] = {}

        for trade in self.trades:
            symbol = trade["symbol"]
            if trade["side"] == "BUY":
                if symbol not in position_map:
                    position_map[symbol] = []
                position_map[symbol].append(trade)
            else:  # SELL
                if symbol in position_map and position_map[symbol]:
                    buy_trade = position_map[symbol].pop(0)
                    profit = (trade["price"] - buy_trade["price"]) * trade["quantity"]
                    profits.append(profit)

        winning_trades = [p for p in profits if p > 0]
        losing_trades = [p for p in profits if p < 0]

        return {
            "total_trades": len(self.trades),
            "buy_trades": len(buys),
            "sell_trades": len(sells),
            "avg_trade_size": avg_trade_size,
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "avg_win": sum(winning_trades) / len(winning_trades) if winning_trades else 0,
            "avg_loss": sum(losing_trades) / len(losing_trades) if losing_trades else 0,
            "profit_factor": abs(sum(winning_trades) / sum(losing_trades)) if losing_trades else float("inf"),
        }

    def generate_report(self, metrics: Optional[List[str]] = None) -> Dict[str, Any]:
        """Generate comprehensive performance report."""
        all_metrics = {
            "sharpe": self.calculate_sharpe_ratio(),
            "sortino": self.calculate_sortino_ratio(),
            "calmar": self.calculate_calmar_ratio(),
            "max_drawdown": self.summary.get("max_drawdown_pct", 0),
            "total_return": self.summary.get("total_return_pct", 0),
            "win_rate": self.summary.get("win_rate", 0) * 100,
        }

        # Add trade analysis
        trade_stats = self.analyze_trades()

        # Filter metrics if specified
        if metrics:
            filtered_metrics = {}
            for metric in metrics:
                if metric.lower() in all_metrics:
                    filtered_metrics[metric] = all_metrics[metric.lower()]
            return {"metrics": filtered_metrics, "trade_stats": trade_stats}

        return {"metrics": all_metrics, "trade_stats": trade_stats}


def format_metric_value(value: float, metric_name: str) -> str:
    """Format metric value for display."""
    if metric_name in ["total_return", "max_drawdown", "win_rate"]:
        return f"{value:.2f}%"
    elif metric_name in ["sharpe", "sortino", "calmar"]:
        if value == float("inf"):
            return "∞"
        elif value == float("-inf"):
            return "-∞"
        return f"{value:.2f}"
    else:
        return f"{value:.2f}"


def fetch_results_from_platform(backtest_id: str) -> Optional[Dict[str, Any]]:
    """Fetch backtest results from Tektii platform."""
    from pathlib import Path

    # Load API configuration
    config_path = Path.home() / ".tektii" / "config.json"
    if not config_path.exists():
        print_colored("No API configuration found. Run 'tektii push --save-config' first", Colors.FAIL)
        return None

    with open(config_path) as f:
        config = json.load(f)

    api_key = config.get("api_key")
    api_url = config.get("api_url", "https://api.tektii.com")

    if not api_key:
        print_colored("No API key configured", Colors.FAIL)
        return None

    # Fetch results from platform
    headers = {"Authorization": f"Bearer {api_key}"}

    try:
        response = requests.get(f"{api_url}/v1/backtests/{backtest_id}/results", headers=headers, timeout=30)

        if response.status_code == 200:
            return cast(Dict[str, Any], response.json())
        elif response.status_code == 404:
            print_colored(f"Backtest {backtest_id} not found", Colors.FAIL)
            return None
        else:
            print_colored(f"Error fetching results: {response.status_code}", Colors.FAIL)
            return None

    except Exception as e:
        print_colored(f"Error connecting to platform: {str(e)}", Colors.FAIL)
        return None


def cmd_analyze(args: Any) -> int:
    """Analyze backtest results from file or platform."""
    print_header("Performance Analysis")

    # Check if we're fetching from platform by ID
    if hasattr(args, "backtest_id") and args.backtest_id:
        print_colored(f"Fetching results for backtest ID: {args.backtest_id}", Colors.OKCYAN)
        results = fetch_results_from_platform(args.backtest_id)

        if not results:
            return 1

        # Optionally save to local file
        if hasattr(args, "save_local") and args.save_local:
            output_file = f"backtest_{args.backtest_id}_results.json"
            with open(output_file, "w") as f:
                json.dump(results, f, indent=2)
            print_colored(f"Results saved to {output_file}", Colors.OKGREEN)
    else:
        # Load from local file
        if not args.results_file:
            print_colored("Error: Either provide a results file or use --backtest-id", Colors.FAIL)
            print("\nUsage:")
            print("  tektii analyze backtest_results.json")
            print("  tektii analyze --backtest-id <ID>")
            return 1

        results_file = args.results_file

        if not os.path.exists(results_file):
            print_colored(f"Error: {results_file} not found", Colors.FAIL)
            print_colored("\nTip: You can also analyze platform results with:", Colors.OKCYAN)
            print("  tektii analyze --backtest-id <ID>")
            return 1

        try:
            with open(results_file, "r") as f:
                results = json.load(f)
        except Exception as e:
            print_colored(f"Error loading results file: {str(e)}", Colors.FAIL)
            return 1

    try:
        # Create analyzer
        assert results is not None  # mypy hint - results is guaranteed non-None here
        analyzer = PerformanceAnalyzer(results)

        # Parse metrics filter
        metrics_filter = None
        if args.metrics and args.metrics.lower() != "all":
            metrics_filter = [m.strip() for m in args.metrics.split(",")]

        # Generate report
        report = analyzer.generate_report(metrics_filter)

        # Display metrics
        print_colored("\nPerformance Metrics:", Colors.HEADER)
        metrics = report.get("metrics", {})
        for metric_name, value in metrics.items():
            formatted_value = format_metric_value(value, metric_name)
            metric_display = metric_name.replace("_", " ").title()
            print(f"  {metric_display}: {formatted_value}")

        # Display trade statistics
        trade_stats = report.get("trade_stats", {})
        if trade_stats:
            print_colored("\nTrade Statistics:", Colors.HEADER)
            print(f"  Total Trades: {trade_stats.get('total_trades', 0)}")
            print(f"  Winning Trades: {trade_stats.get('winning_trades', 0)}")
            print(f"  Losing Trades: {trade_stats.get('losing_trades', 0)}")
            print(f"  Average Win: ${trade_stats.get('avg_win', 0):,.2f}")
            print(f"  Average Loss: ${trade_stats.get('avg_loss', 0):,.2f}")
            profit_factor = trade_stats.get("profit_factor", 0)
            pf_display = "∞" if profit_factor == float("inf") else f"{profit_factor:.2f}"
            print(f"  Profit Factor: {pf_display}")

        # Period information
        period = results.get("period", {})
        if period:
            print_colored("\nBacktest Period:", Colors.HEADER)
            print(f"  Start: {period.get('start', 'N/A')}")
            print(f"  End: {period.get('end', 'N/A')}")
            print(f"  Duration: {period.get('days', 0)} days")

        # Export if requested
        if args.export:
            export_format = args.export.lower()
            # Handle export filename based on source
            if hasattr(args, "backtest_id") and args.backtest_id:
                export_file = f"backtest_{args.backtest_id}_analysis.{export_format}"
            else:
                export_file = args.results_file.replace(".json", f"_analysis.{export_format}")

            if export_format == "csv":
                # Simple CSV export
                import csv

                with open(export_file, "w", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Metric", "Value"])
                    for metric, value in metrics.items():
                        writer.writerow([metric, value])
                print_colored(f"\n✓ Analysis exported to {export_file}", Colors.OKGREEN)
            else:
                print_colored(f"Export format '{export_format}' not yet implemented", Colors.WARNING)

        # Plot suggestion
        if args.plot:
            print_colored("\n✓ Plotting functionality coming soon!", Colors.OKCYAN)
            print("  Use the equity_curve data in the results file to create custom plots")

        return 0

    except Exception as e:
        print_colored(f"Error: {e}", Colors.FAIL)
        import traceback

        traceback.print_exc()
        return 1
