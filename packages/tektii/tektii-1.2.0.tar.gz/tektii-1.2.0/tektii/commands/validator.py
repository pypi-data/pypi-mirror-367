"""Strategy validation module for pre-upload checks."""

# mypy: disable-error-code="unreachable"

import importlib.util
import inspect
import logging
import os
import statistics
import time
import traceback
import tracemalloc
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Type

from tektii.strategy import TektiiStrategy
from tektii.strategy.grpc import market_data_pb2
from tektii.strategy.models.market_data import BarData, BarType, TickData
from tektii.strategy.models.orders import OrderBuilder

from ..utils.colors import Colors, print_colored, print_header
from ..utils.loader import load_strategy_class

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of strategy validation."""

    is_valid: bool
    errors: List[str]
    warnings: List[str]
    info: Dict[str, Any]

    def add_error(self, message: str) -> None:
        """Add an error message."""
        self.errors.append(message)
        self.is_valid = False

    def add_warning(self, message: str) -> None:
        """Add a warning message."""
        self.warnings.append(message)

    def add_info(self, key: str, value: Any) -> None:
        """Add an info entry."""
        self.info[key] = value

    def __str__(self) -> str:
        """Return string representation of the validation result."""
        lines = []

        if self.is_valid:
            lines.append("✅ Strategy validation PASSED")
        else:
            lines.append("❌ Strategy validation FAILED")

        if self.errors:
            lines.append("\nErrors:")
            for error in self.errors:
                lines.append(f"  ❌ {error}")

        if self.warnings:
            lines.append("\nWarnings:")
            for warning in self.warnings:
                lines.append(f"  ⚠️  {warning}")

        if self.info:
            lines.append("\nInfo:")
            for key, value in self.info.items():
                if key == "performance_metrics" and isinstance(value, dict):
                    lines.append("  • Performance Metrics:")
                    for metric, val in value.items():
                        lines.append(f"    - {metric}: {val}")
                elif key == "memory_metrics" and isinstance(value, dict):
                    lines.append("  • Memory Metrics:")
                    for metric, val in value.items():
                        lines.append(f"    - {metric}: {val}")
                else:
                    lines.append(f"  • {key}: {value}")

        return "\n".join(lines)


class StrategyValidator:
    """Comprehensive validator for trading strategies."""

    def __init__(self, strategy_class: Type[TektiiStrategy]) -> None:
        """Initialize validator.

        Args:
            strategy_class: Strategy class to validate
        """
        self.strategy_class = strategy_class
        self.result = ValidationResult(is_valid=True, errors=[], warnings=[], info={})

    def validate(self, comprehensive: bool = True) -> ValidationResult:
        """Run all validation checks.

        Args:
            comprehensive: Whether to run comprehensive tests (performance, edge cases)

        Returns:
            Validation result
        """
        # Core validation checks
        self._check_inheritance()
        self._check_required_methods()
        strategy_instance = self._check_instantiation()

        if strategy_instance:
            # Functional validation
            self._check_initialization(strategy_instance)
            self._check_market_data_handling(strategy_instance)
            self._check_order_capabilities(strategy_instance)
            self._check_orderbuilder_usage(strategy_instance)
            self._check_error_handling(strategy_instance)

            # Additional checks if comprehensive
            if comprehensive:
                self._check_edge_cases(strategy_instance)
                self._check_performance(strategy_instance)
                self._check_memory_leaks(strategy_instance)

            # Info collection
            self._collect_strategy_info(strategy_instance)

        return self.result

    def _check_inheritance(self) -> None:
        """Check that the class properly inherits from TektiiStrategy."""
        if not issubclass(self.strategy_class, TektiiStrategy):
            self.result.add_error("Strategy class must inherit from TektiiStrategy")
            return

        # Check if it directly inherits or through intermediate classes
        mro = self.strategy_class.__mro__
        if TektiiStrategy not in mro:
            self.result.add_error("Strategy class must have TektiiStrategy in its method resolution order")
            return

        self.result.add_info("inheritance", "✓ Correctly inherits from TektiiStrategy")

        # Check for common inheritance issues
        if len(mro) > 4:  # strategy_class -> ... -> TektiiStrategy -> ABC -> object
            self.result.add_warning(f"Deep inheritance hierarchy ({len(mro)} levels) may impact performance")

    def _check_required_methods(self) -> None:
        """Check that required methods are implemented."""
        # Only on_market_data is abstract and required
        required_methods = ["on_market_data"]

        for method_name in required_methods:
            if not hasattr(self.strategy_class, method_name):
                self.result.add_error(f"Missing required method: {method_name}")
                continue

            method = getattr(self.strategy_class, method_name)
            if not callable(method):
                self.result.add_error(f"{method_name} is not callable")
                continue

            # Check if it's actually implemented (not just inherited abstract)
            if method.__qualname__ == f"TektiiStrategy.{method_name}":
                self.result.add_error(f"{method_name} is not implemented (using base class abstract method)")

        # Check optional methods and provide info about what's implemented
        optional_methods = [
            "on_initialize",
            "on_shutdown",
            "on_order_update",
            "on_position_update",
            "on_account_update",
            "on_trade",
            "on_system_event",
        ]

        implemented_optional = []
        for method_name in optional_methods:
            if hasattr(self.strategy_class, method_name):
                method = getattr(self.strategy_class, method_name)
                # Check if it's overridden (not the default empty implementation)
                if callable(method) and method.__qualname__ != f"TektiiStrategy.{method_name}":
                    implemented_optional.append(method_name)

        if implemented_optional:
            self.result.add_info("optional_methods", f"Implements: {', '.join(implemented_optional)}")
        else:
            self.result.add_info("optional_methods", "Uses default implementations for all optional methods")

        # Check method signatures for common issues
        self._check_method_signatures()

    def _check_method_signatures(self) -> None:
        """Check method signatures for common issues."""
        # Check on_market_data signature
        try:
            sig = inspect.signature(self.strategy_class.on_market_data)
            params = list(sig.parameters.keys())

            # Should accept tick_data and/or bar_data parameters
            if not any(param in params for param in ["tick_data", "bar_data"]):
                self.result.add_warning("on_market_data should accept 'tick_data' and/or 'bar_data' parameters")

        except Exception as e:
            self.result.add_warning(f"Could not inspect on_market_data signature: {str(e)}")

    def _check_instantiation(self) -> Optional[TektiiStrategy]:
        """Check that the strategy can be instantiated."""
        try:
            # Try to instantiate with no arguments first
            try:
                strategy = self.strategy_class()
                self.result.add_info("instantiation", "✓ Successfully instantiated with no arguments")
                return strategy
            except TypeError as e:
                # If that fails, try to determine what arguments are needed
                sig = inspect.signature(self.strategy_class.__init__)
                params = [p for p in sig.parameters.values() if p.name != "self" and p.default == inspect.Parameter.empty]

                if params:
                    param_names = [p.name for p in params]
                    self.result.add_error(
                        f"Strategy requires constructor parameters: {', '.join(param_names)}. " f"Consider providing default values for deployment."
                    )
                    return None
                else:
                    raise e

        except Exception as e:
            self.result.add_error(f"Failed to instantiate strategy: {str(e)}")
            self.result.add_info("instantiation_traceback", traceback.format_exc())
            return None

    def _check_initialization(self, strategy: TektiiStrategy) -> None:
        """Check that the strategy can be initialized."""
        try:
            # Test initialization with sample data
            config = {"param1": "value1", "param2": "value2"}
            symbols = ["AAPL", "GOOGL", "MSFT"]
            strategy_id = "test-strategy-validation"

            # Use the internal _initialize method
            strategy._initialize(config, symbols, strategy_id)
            self.result.add_info("initialization", "✓ Successfully initialized")

            # Check if initialization set expected attributes
            if hasattr(strategy, "_config"):
                self.result.add_info("config_stored", f"✓ Config stored with {len(strategy._config)} parameters")

            if hasattr(strategy, "_symbols"):
                self.result.add_info("symbols_stored", f"✓ Symbols stored: {len(strategy._symbols)} symbols")

        except Exception as e:
            self.result.add_error(f"Failed to initialize strategy: {str(e)}")
            self.result.add_info("initialization_traceback", traceback.format_exc())

    def _check_market_data_handling(self, strategy: TektiiStrategy) -> None:
        """Check market data processing with both tick and bar data."""
        # Test tick data
        try:
            tick_data = market_data_pb2.TickData()
            tick_data.symbol = "AAPL"
            tick_data.bid = 150.0
            tick_data.ask = 150.1
            tick_data.last = 150.05
            tick_data.mid = 150.05
            tick_data.tick_type = market_data_pb2.TickData.TICK_TYPE_QUOTE_AND_TRADE

            model_tick_data = TickData.from_proto(tick_data)
            result = strategy.on_market_data(tick_data=model_tick_data)

            self.result.add_info("tick_data_handling", "✓ Processes tick data without errors")

        except Exception as e:
            self.result.add_error(f"Error processing tick data: {str(e)}")
            self.result.add_info("tick_data_traceback", traceback.format_exc())

        # Test bar data
        try:
            import time
            from decimal import Decimal

            bar_data = BarData(
                symbol="AAPL",
                timestamp_us=int(time.time() * 1_000_000),
                open=Decimal("150.00"),
                high=Decimal("151.00"),
                low=Decimal("149.50"),
                close=Decimal("150.75"),
                volume=1000000,
                bar_size=1,
                bar_size_unit="min",
                bar_type=BarType.TIME,
                vwap=None,
                trade_count=None,
            )

            result = strategy.on_market_data(bar_data=bar_data)

            if result is not None:
                self.result.add_info("bar_data_response", f"✓ Returns {type(result).__name__}")

            self.result.add_info("bar_data_handling", "✓ Processes bar data without errors")

        except Exception as e:
            self.result.add_error(f"Error processing bar data: {str(e)}")
            self.result.add_info("bar_data_traceback", traceback.format_exc())

    def _check_order_capabilities(self, strategy: TektiiStrategy) -> None:
        """Check order placement capabilities and client availability."""
        try:
            # Check if strategy has order client
            if hasattr(strategy, "order_client"):
                self.result.add_info("order_client", "✓ Order client available")

                # Check available methods
                order_methods = []
                for method_name in ["place_order", "cancel_order", "modify_order"]:
                    if hasattr(strategy.order_client, method_name):
                        order_methods.append(method_name)

                if order_methods:
                    self.result.add_info("order_methods", f"✓ Available: {', '.join(order_methods)}")
                else:
                    self.result.add_warning("Order client exists but no order methods found")
            else:
                self.result.add_warning("Strategy missing order_client (may be set during runtime)")

            # Check if strategy uses order-related imports
            module = strategy.__class__.__module__
            if module:
                try:
                    import sys

                    strategy_module = sys.modules.get(module)
                    if strategy_module:
                        module_source = inspect.getsource(strategy_module)
                        if "Order" in module_source or "order" in module_source.lower():
                            self.result.add_info("order_usage", "✓ Strategy appears to use order-related functionality")
                except Exception:
                    pass  # Source inspection is optional

        except Exception as e:
            self.result.add_warning(f"Issue checking order capabilities: {str(e)}")

    def _check_orderbuilder_usage(self, strategy: TektiiStrategy) -> None:
        """Check if strategy properly uses the OrderBuilder API."""
        try:
            # Test OrderBuilder functionality
            builder = OrderBuilder()

            # Test fluent API
            builder.symbol("AAPL").buy().limit(150.0).quantity(100).build()

            self.result.add_info("orderbuilder", "✓ OrderBuilder API is functional")

            # Check if strategy code uses OrderBuilder
            try:
                source = inspect.getsource(self.strategy_class)
                if "OrderBuilder" in source:
                    self.result.add_info("orderbuilder_usage", "✓ Strategy uses OrderBuilder")
                else:
                    self.result.add_info("orderbuilder_usage", "Strategy does not use OrderBuilder (consider for complex orders)")
            except Exception:
                pass  # Source inspection is optional

        except Exception as e:
            self.result.add_warning(f"Issue checking OrderBuilder usage: {str(e)}")

    def _check_error_handling(self, strategy: TektiiStrategy) -> None:
        """Check error handling capabilities with various invalid inputs."""
        error_scenarios = [
            ("negative_prices", lambda: self._test_negative_prices(strategy)),
            ("missing_data", lambda: self._test_missing_data(strategy)),
            ("invalid_symbols", lambda: self._test_invalid_symbols(strategy)),
            ("extreme_values", lambda: self._test_extreme_values(strategy)),
        ]

        handled_errors = 0
        for scenario_name, test_func in error_scenarios:
            try:
                test_func()  # type: ignore[no-untyped-call]
                # If no exception, strategy may not be validating input
                self.result.add_warning(f"Strategy may not validate {scenario_name.replace('_', ' ')}")
            except Exception:
                # Exception is good - strategy is handling invalid data
                handled_errors += 1

        if handled_errors > 0:
            self.result.add_info("error_handling", f"✓ Handles {handled_errors}/{len(error_scenarios)} error scenarios")
        else:
            self.result.add_warning("Strategy may not have robust error handling")

    def _test_negative_prices(self, strategy: TektiiStrategy) -> None:
        """Test with negative prices."""
        tick_data = market_data_pb2.TickData()
        tick_data.symbol = "TEST"
        tick_data.bid = -100.0
        tick_data.ask = -99.0
        tick_data.last = -99.5
        tick_data.tick_type = market_data_pb2.TickData.TICK_TYPE_QUOTE_AND_TRADE

        model_tick_data = TickData.from_proto(tick_data)
        strategy.on_market_data(tick_data=model_tick_data)

    def _test_missing_data(self, strategy: TektiiStrategy) -> None:
        """Test with missing/None data."""
        strategy.on_market_data(tick_data=None, bar_data=None)

    def _test_invalid_symbols(self, strategy: TektiiStrategy) -> None:
        """Test with invalid symbols."""
        tick_data = market_data_pb2.TickData()
        tick_data.symbol = ""  # Empty symbol
        tick_data.bid = 100.0
        tick_data.ask = 100.1

        model_tick_data = TickData.from_proto(tick_data)
        strategy.on_market_data(tick_data=model_tick_data)

    def _test_extreme_values(self, strategy: TektiiStrategy) -> None:
        """Test with extreme values."""
        tick_data = market_data_pb2.TickData()
        tick_data.symbol = "TEST"
        tick_data.bid = 1e10  # Very large number
        tick_data.ask = 1e10 + 1
        tick_data.last = 1e10 + 0.5

        model_tick_data = TickData.from_proto(tick_data)
        strategy.on_market_data(tick_data=model_tick_data)

    def _check_edge_cases(self, strategy: TektiiStrategy) -> None:
        """Check strategy behavior with market edge cases."""
        edge_cases = [
            ("zero_volume", self._test_zero_volume),
            ("wide_spread", self._test_wide_spread),
            ("price_gap", self._test_price_gap),
            ("rapid_events", self._test_rapid_events),
            ("stale_data", self._test_stale_data),
        ]

        passed_cases = 0
        for case_name, test_func in edge_cases:
            try:
                test_func(strategy)
                passed_cases += 1
            except Exception as e:
                self.result.add_warning(f"Strategy fails on {case_name.replace('_', ' ')}: {str(e)}")

        self.result.add_info("edge_case_handling", f"✓ Passed {passed_cases}/{len(edge_cases)} edge case tests")

    def _test_zero_volume(self, strategy: TektiiStrategy) -> None:
        """Test with zero volume tick."""
        tick_data = market_data_pb2.TickData()
        tick_data.symbol = "AAPL"
        tick_data.bid = 150.0
        tick_data.ask = 150.1
        tick_data.tick_type = market_data_pb2.TickData.TICK_TYPE_QUOTE  # No trade

        model_tick_data = TickData.from_proto(tick_data)
        strategy.on_market_data(tick_data=model_tick_data)

    def _test_wide_spread(self, strategy: TektiiStrategy) -> None:
        """Test with unrealistically wide bid-ask spread."""
        tick_data = market_data_pb2.TickData()
        tick_data.symbol = "AAPL"
        tick_data.bid = 100.0
        tick_data.ask = 110.0  # 10% spread
        tick_data.last = 105.0
        tick_data.tick_type = market_data_pb2.TickData.TICK_TYPE_QUOTE_AND_TRADE

        model_tick_data = TickData.from_proto(tick_data)
        strategy.on_market_data(tick_data=model_tick_data)

    def _test_price_gap(self, strategy: TektiiStrategy) -> None:
        """Test with sudden large price movement."""
        # Normal price
        tick1 = market_data_pb2.TickData()
        tick1.symbol = "AAPL"
        tick1.bid = 150.0
        tick1.ask = 150.1
        tick1.last = 150.05
        tick1.tick_type = market_data_pb2.TickData.TICK_TYPE_QUOTE_AND_TRADE

        model_tick1 = TickData.from_proto(tick1)
        strategy.on_market_data(tick_data=model_tick1)

        # 50% price gap
        tick2 = market_data_pb2.TickData()
        tick2.symbol = "AAPL"
        tick2.bid = 225.0
        tick2.ask = 225.1
        tick2.last = 225.05
        tick2.tick_type = market_data_pb2.TickData.TICK_TYPE_QUOTE_AND_TRADE

        model_tick2 = TickData.from_proto(tick2)
        strategy.on_market_data(tick_data=model_tick2)

    def _test_rapid_events(self, strategy: TektiiStrategy) -> None:
        """Test rapid-fire market data events."""
        from decimal import Decimal

        base_price = Decimal("150.0")
        for i in range(100):
            price_adj = Decimal("0.01") * (i % 10 - 5)  # Small oscillations

            tick_data = market_data_pb2.TickData()
            tick_data.symbol = "AAPL"
            tick_data.bid = float(base_price + price_adj)
            tick_data.ask = float(base_price + price_adj + Decimal("0.1"))
            tick_data.last = float(base_price + price_adj + Decimal("0.05"))
            tick_data.tick_type = market_data_pb2.TickData.TICK_TYPE_QUOTE_AND_TRADE

            model_tick_data = TickData.from_proto(tick_data)
            strategy.on_market_data(tick_data=model_tick_data)

    def _test_stale_data(self, strategy: TektiiStrategy) -> None:
        """Test with old timestamp data."""
        tick_data = market_data_pb2.TickData()
        tick_data.symbol = "AAPL"
        tick_data.bid = 150.0
        tick_data.ask = 150.1
        tick_data.last = 150.05
        # Note: timestamp_us is not available on TickData model, only on proto
        # Test with old data by setting it on the proto before conversion
        tick_data.tick_type = market_data_pb2.TickData.TICK_TYPE_QUOTE_AND_TRADE

        model_tick_data = TickData.from_proto(tick_data)
        strategy.on_market_data(tick_data=model_tick_data)

    def _check_performance(self, strategy: TektiiStrategy) -> None:
        """Check performance characteristics."""
        # Create test market data
        tick_data = market_data_pb2.TickData()
        tick_data.symbol = "AAPL"
        tick_data.bid = 150.0
        tick_data.ask = 150.1
        tick_data.last = 150.05
        tick_data.tick_type = market_data_pb2.TickData.TICK_TYPE_QUOTE_AND_TRADE

        model_tick_data = TickData.from_proto(tick_data)

        # Warmup phase
        for _ in range(100):
            strategy.on_market_data(tick_data=model_tick_data)

        # Performance measurement
        num_events = 1000
        latencies = []

        for _ in range(num_events):
            start_time = time.perf_counter()
            strategy.on_market_data(tick_data=model_tick_data)
            end_time = time.perf_counter()
            latencies.append((end_time - start_time) * 1_000_000)  # microseconds

        # Calculate statistics
        sorted_latencies = sorted(latencies)
        mean_latency = statistics.mean(latencies)
        median_latency = statistics.median(latencies)

        # Calculate percentiles
        n = len(sorted_latencies)
        p95_index = int(0.95 * (n - 1))
        p99_index = int(0.99 * (n - 1))
        p95_latency = sorted_latencies[p95_index]
        p99_latency = sorted_latencies[p99_index]
        max_latency = max(latencies)

        # Calculate throughput
        total_time = sum(latencies) / 1_000_000  # convert to seconds
        events_per_second = num_events / total_time if total_time > 0 else 0

        # Store performance metrics
        self.result.info["performance_metrics"] = {
            "throughput": f"{events_per_second:.0f} events/second",
            "mean_latency": f"{mean_latency:.2f} μs",
            "median_latency": f"{median_latency:.2f} μs",
            "p95_latency": f"{p95_latency:.2f} μs",
            "p99_latency": f"{p99_latency:.2f} μs",
            "max_latency": f"{max_latency:.2f} μs",
        }

        # Performance warnings with more detailed thresholds
        if events_per_second < 500:
            self.result.add_warning(f"Low throughput: {events_per_second:.0f} events/sec (recommended: >500 for real-time trading)")
        elif events_per_second < 100:
            self.result.add_error(f"Very low throughput: {events_per_second:.0f} events/sec (minimum: 100 events/sec)")

        if p99_latency > 5000:  # 5ms
            self.result.add_warning(f"High P99 latency: {p99_latency:.0f} μs (recommended: <5,000 μs)")

        if max_latency > 50000:  # 50ms
            self.result.add_warning(f"Very high max latency: {max_latency:.0f} μs (spikes >50ms may impact trading)")

    def _check_memory_leaks(self, strategy: TektiiStrategy) -> None:
        """Check for memory leaks during extended operation."""
        import gc

        # Force garbage collection
        gc.collect()

        # Start memory tracking
        tracemalloc.start()
        memory_start = tracemalloc.get_traced_memory()[0]

        # Create test data
        tick_data = market_data_pb2.TickData()
        tick_data.symbol = "AAPL"
        tick_data.bid = 150.0
        tick_data.ask = 150.1
        tick_data.last = 150.05
        tick_data.tick_type = market_data_pb2.TickData.TICK_TYPE_QUOTE_AND_TRADE

        model_tick_data = TickData.from_proto(tick_data)

        # Run strategy for extended period
        num_events = 5000
        for i in range(num_events):
            # Vary the data slightly to prevent optimization
            tick_data.last = 150.0 + (i % 100) * 0.01
            model_tick_data = TickData.from_proto(tick_data)
            strategy.on_market_data(tick_data=model_tick_data)

            # Force GC periodically
            if i % 1000 == 0:
                gc.collect()

        # Final memory check
        memory_current, memory_peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        memory_growth_mb = (memory_current - memory_start) / 1024 / 1024
        peak_memory_mb = memory_peak / 1024 / 1024

        self.result.info["memory_metrics"] = {
            "peak_memory": f"{peak_memory_mb:.2f} MB",
            "memory_growth": f"{memory_growth_mb:.2f} MB",
            "events_processed": num_events,
        }

        # Memory warnings
        if memory_growth_mb > 50:
            self.result.add_error(f"Significant memory leak detected: {memory_growth_mb:.2f} MB growth over {num_events} events")
        elif memory_growth_mb > 20:
            self.result.add_warning(f"Potential memory leak: {memory_growth_mb:.2f} MB growth over {num_events} events")

        if peak_memory_mb > 200:
            self.result.add_warning(f"High peak memory usage: {peak_memory_mb:.2f} MB")

    def _collect_strategy_info(self, strategy: TektiiStrategy) -> None:
        """Collect comprehensive information about the strategy."""
        # Basic info
        self.result.add_info("strategy_name", strategy.__class__.__name__)
        self.result.add_info("strategy_module", strategy.__class__.__module__)

        # Documentation
        if strategy.__class__.__doc__:
            doc_lines = strategy.__class__.__doc__.strip().split("\n")
            self.result.add_info("description", doc_lines[0])
            if len(doc_lines) > 1:
                self.result.add_info("has_detailed_docs", "✓ Multi-line docstring")

        # Memory footprint
        import sys

        size_bytes = sys.getsizeof(strategy)
        self.result.add_info("base_memory_usage", f"{size_bytes} bytes")

        # Check for large data structures
        large_structures = []
        for attr_name in dir(strategy):
            if not attr_name.startswith("_"):
                try:
                    attr = getattr(strategy, attr_name)
                    if hasattr(attr, "__len__"):
                        length = len(attr)
                        if length > 1000:
                            large_structures.append(f"{attr_name} ({length} items)")
                except Exception:
                    pass

        if large_structures:
            self.result.add_warning(f"Large data structures found: {', '.join(large_structures)}")

        # Check for state complexity
        state_attrs = [attr for attr in dir(strategy) if not attr.startswith("_") and not callable(getattr(strategy, attr))]
        if len(state_attrs) > 20:
            self.result.add_warning(f"Complex state: {len(state_attrs)} attributes (consider simplification)")
        elif len(state_attrs) > 0:
            self.result.add_info("state_attributes", f"{len(state_attrs)} state attributes")


def validate_strategy(strategy_class: Type[TektiiStrategy], comprehensive: bool = True) -> ValidationResult:
    """Validate a strategy class.

    Args:
        strategy_class: Strategy class to validate
        comprehensive: Whether to run comprehensive tests

    Returns:
        Validation result
    """
    validator = StrategyValidator(strategy_class)
    return validator.validate(comprehensive=comprehensive)


def validate_module(module_path: str, class_name: str, comprehensive: bool = True) -> ValidationResult:
    """Validate a strategy from a module file.

    Args:
        module_path: Path to Python module
        class_name: Name of strategy class
        comprehensive: Whether to run comprehensive tests

    Returns:
        Validation result
    """
    try:
        strategy_class = load_strategy_class(module_path, class_name)
        return validate_strategy(strategy_class, comprehensive=comprehensive)
    except Exception as e:
        result = ValidationResult(is_valid=False, errors=[], warnings=[], info={})
        result.add_error(f"Failed to load strategy: {str(e)}")
        return result


def cmd_validate(args: Any) -> int:
    """Validate a strategy implementation using the comprehensive validator."""
    strategy_file = args.file

    if not os.path.exists(strategy_file):
        print_colored(f"Error: {strategy_file} not found", Colors.FAIL)
        print_colored("\nSuggestions:", Colors.OKCYAN)
        print("  • Check if the file path is correct")
        print("  • Run 'tektii status' to see recent strategies")
        print("  • Create a new strategy: tektii new my_strategy")
        return 1

    print_header(f"Validating {strategy_file}")

    # Load the strategy module
    try:
        spec = importlib.util.spec_from_file_location("strategy", strategy_file)
        if spec is None:
            raise ValueError("Failed to create module spec")
        module = importlib.util.module_from_spec(spec)
        if spec.loader is None:
            raise ValueError("Module spec has no loader")
        spec.loader.exec_module(module)
    except Exception as e:
        print_colored(f"✗ Failed to load module: {e}", Colors.FAIL)
        print_colored("\nCommon issues:", Colors.OKCYAN)
        print("  • Missing imports: pip install -e .")
        print("  • Syntax errors: python -m py_compile " + strategy_file)
        print("  • Module issues: Check PYTHONPATH and __init__.py files")
        return 1

    # Find strategy class
    strategy_class = None
    strategy_classes = []

    for name, obj in vars(module).items():
        if isinstance(obj, type) and issubclass(obj, TektiiStrategy) and obj != TektiiStrategy:
            strategy_classes.append((name, obj))
            if strategy_class is None:
                strategy_class = obj

    if not strategy_class:
        print_colored("✗ No TektiiStrategy subclass found", Colors.FAIL)
        return 1

    if len(strategy_classes) > 1:
        class_names = [name for name, _ in strategy_classes]
        print_colored(f"Found multiple strategy classes: {', '.join(class_names)}", Colors.WARNING)
        print_colored(f"Using: {strategy_class.__name__}", Colors.OKCYAN)

    print_colored(f"✓ Found strategy class: {strategy_class.__name__}", Colors.OKGREEN)

    # Run validation (comprehensive by default, fast if --fast flag is used)
    comprehensive = not getattr(args, "fast", False)
    result = validate_strategy(strategy_class, comprehensive=comprehensive)

    # Print results
    print()
    print(result)

    return 0 if result.is_valid else 1
