"""Unit tests for strategy lifecycle management."""

from __future__ import annotations

import threading
import time
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import MagicMock

import pytest

from tektii.strategy.base import TektiiStrategy
from tektii.strategy.models import SystemEvent, SystemEventType, TickData


class LifecycleTestStrategy(TektiiStrategy):
    """Test strategy for lifecycle testing."""

    def __init__(self):
        super().__init__()
        self.initialized = False
        self.shutdown = False
        self.config = None
        self.symbols = None
        self.market_data_count = 0
        self.errors = []
        self.initialization_thread = None
        self.shutdown_thread = None

    def on_market_data(self, tick_data: TickData | None = None, bar_data=None) -> None:
        self.market_data_count += 1

    def on_initialize(self, config: dict[str, str], symbols: list[str]) -> None:
        self.initialized = True
        self.config = config
        self.symbols = symbols
        self.initialization_thread = threading.current_thread().name

    def on_shutdown(self) -> None:
        self.shutdown = True
        self.shutdown_thread = threading.current_thread().name

    def on_error(self, error: Exception) -> None:
        self.errors.append(error)


class TestStrategyLifecycle:
    """Test suite for strategy lifecycle management."""

    def test_strategy_initialization(self):
        """Test strategy initialization process."""
        strategy = LifecycleTestStrategy()

        assert not strategy.initialized
        assert strategy.config is None
        assert strategy.symbols is None

        config = {"param1": "value1", "param2": "value2"}
        symbols = ["AAPL", "GOOGL", "MSFT"]

        strategy.on_initialize(config, symbols)

        assert strategy.initialized
        assert strategy.config == config
        assert strategy.symbols == symbols

    def test_strategy_shutdown(self):
        """Test strategy shutdown process."""
        strategy = LifecycleTestStrategy()

        assert not strategy.shutdown

        strategy.on_shutdown()

        assert strategy.shutdown

    def test_initialization_with_empty_config(self):
        """Test initialization with empty configuration."""
        strategy = LifecycleTestStrategy()

        strategy.on_initialize({}, [])

        assert strategy.initialized
        assert strategy.config == {}
        assert strategy.symbols == []

    def test_initialization_with_state_setup(self):
        """Test that initialization properly sets up internal state."""
        strategy = LifecycleTestStrategy()

        # Check initial state
        assert hasattr(strategy, "_positions")
        assert hasattr(strategy, "_orders")
        assert hasattr(strategy, "_account")
        assert strategy._positions == {}
        assert strategy._orders == {}
        assert strategy._account is None

        # Initialize and verify state is preserved
        strategy.on_initialize({"key": "value"}, ["AAPL"])

        assert strategy._positions == {}
        assert strategy._orders == {}
        assert strategy._account is None

    def test_multiple_initialization_calls(self):
        """Test behavior with multiple initialization calls."""
        strategy = LifecycleTestStrategy()

        # First initialization
        config1 = {"version": "1"}
        symbols1 = ["AAPL"]
        strategy.on_initialize(config1, symbols1)

        assert strategy.config == config1
        assert strategy.symbols == symbols1

        # Second initialization (should override)
        config2 = {"version": "2"}
        symbols2 = ["AAPL", "GOOGL"]
        strategy.on_initialize(config2, symbols2)

        assert strategy.config == config2
        assert strategy.symbols == symbols2

    def test_initialization_error_handling(self):
        """Test error handling during initialization."""

        class ErrorStrategy(TektiiStrategy):
            def on_market_data(self, tick_data=None, bar_data=None):
                pass

            def on_initialize(self, config, symbols):
                raise ValueError("Initialization failed")

        strategy = ErrorStrategy()

        # Should raise the error
        with pytest.raises(ValueError, match="Initialization failed"):
            strategy.on_initialize({}, [])

    def test_shutdown_cleanup(self):
        """Test that shutdown properly cleans up resources."""

        class CleanupStrategy(TektiiStrategy):
            def __init__(self):
                super().__init__()
                self.resource = MagicMock()
                self.cleaned_up = False

            def on_market_data(self, tick_data=None, bar_data=None):
                pass

            def on_shutdown(self):
                self.resource.close()
                self.cleaned_up = True

        strategy = CleanupStrategy()
        strategy.on_shutdown()

        assert strategy.cleaned_up
        strategy.resource.close.assert_called_once()

    def test_lifecycle_with_active_orders(self):
        """Test lifecycle with active orders."""
        strategy = LifecycleTestStrategy()

        # Add some mock orders
        strategy._orders = {"order1": MagicMock(id="order1", status="PENDING"), "order2": MagicMock(id="order2", status="FILLED")}

        # Shutdown should handle active orders gracefully
        strategy.on_shutdown()
        assert strategy.shutdown

    def test_lifecycle_with_open_positions(self):
        """Test lifecycle with open positions."""
        strategy = LifecycleTestStrategy()

        # Add some mock positions
        strategy._positions = {"AAPL": MagicMock(symbol="AAPL", quantity=100), "GOOGL": MagicMock(symbol="GOOGL", quantity=50)}

        # Shutdown should handle open positions gracefully
        strategy.on_shutdown()
        assert strategy.shutdown

    def test_concurrent_lifecycle_operations(self):
        """Test thread safety of lifecycle operations."""
        strategy = LifecycleTestStrategy()
        results = []

        def initialize_task():
            strategy.on_initialize({"thread": "init"}, ["AAPL"])
            results.append("init")

        def process_data_task():
            for _ in range(10):
                strategy.on_market_data(MagicMock())
            results.append("data")

        def shutdown_task():
            time.sleep(0.01)  # Small delay to ensure other threads start
            strategy.on_shutdown()
            results.append("shutdown")

        # Run tasks concurrently
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(initialize_task), executor.submit(process_data_task), executor.submit(shutdown_task)]

            for future in futures:
                future.result()

        # Verify all tasks completed
        assert "init" in results
        assert "data" in results
        assert "shutdown" in results
        assert strategy.initialized
        assert strategy.shutdown
        assert strategy.market_data_count == 10

    def test_lifecycle_state_transitions(self):
        """Test valid state transitions during lifecycle."""

        class StateStrategy(TektiiStrategy):
            def __init__(self):
                super().__init__()
                self.state = "CREATED"
                self.state_history = ["CREATED"]

            def on_market_data(self, tick_data=None, bar_data=None):
                if self.state == "INITIALIZED":
                    self.state = "RUNNING"
                    self.state_history.append("RUNNING")

            def on_initialize(self, config, symbols):
                self.state = "INITIALIZED"
                self.state_history.append("INITIALIZED")

            def on_shutdown(self):
                self.state = "SHUTDOWN"
                self.state_history.append("SHUTDOWN")

        strategy = StateStrategy()

        # Test state transitions
        assert strategy.state == "CREATED"

        strategy.on_initialize({}, ["AAPL"])
        assert strategy.state == "INITIALIZED"

        strategy.on_market_data(MagicMock())
        assert strategy.state == "RUNNING"

        strategy.on_shutdown()
        assert strategy.state == "SHUTDOWN"

        # Verify complete state history
        assert strategy.state_history == ["CREATED", "INITIALIZED", "RUNNING", "SHUTDOWN"]

    def test_initialization_with_broker_connection(self):
        """Test initialization with broker connection setup."""

        class BrokerStrategy(TektiiStrategy):
            def __init__(self):
                super().__init__()
                self.broker_connected = False

            def on_market_data(self, tick_data=None, bar_data=None):
                pass

            def on_initialize(self, config, symbols):
                # Simulate broker connection
                if "broker_url" in config:
                    self.broker_connected = True

            def on_system_event(self, event: SystemEvent):
                if event.type == SystemEventType.CONNECTED:
                    self.broker_connected = True
                elif event.type == SystemEventType.DISCONNECTED:
                    self.broker_connected = False

        strategy = BrokerStrategy()

        # Initialize without broker config
        strategy.on_initialize({}, ["AAPL"])
        assert not strategy.broker_connected

        # Initialize with broker config
        strategy.on_initialize({"broker_url": "tcp://localhost:5555"}, ["AAPL"])
        assert strategy.broker_connected

    def test_graceful_shutdown_with_pending_operations(self):
        """Test graceful shutdown with pending operations."""

        class PendingOpsStrategy(TektiiStrategy):
            def __init__(self):
                super().__init__()
                self.pending_operations = []
                self.operations_cancelled = False

            def on_market_data(self, tick_data=None, bar_data=None):
                self.pending_operations.append("market_data")

            def on_shutdown(self):
                # Cancel all pending operations
                if self.pending_operations:
                    self.operations_cancelled = True
                    self.pending_operations.clear()

        strategy = PendingOpsStrategy()

        # Add some pending operations
        for _ in range(5):
            strategy.on_market_data(MagicMock())

        assert len(strategy.pending_operations) == 5

        # Shutdown should cancel operations
        strategy.on_shutdown()
        assert strategy.operations_cancelled
        assert len(strategy.pending_operations) == 0

    def test_error_recovery_during_lifecycle(self):
        """Test error recovery during lifecycle phases."""

        class RecoveryStrategy(TektiiStrategy):
            def __init__(self):
                super().__init__()
                self.recovered = False
                self.error_count = 0

            def on_market_data(self, tick_data=None, bar_data=None):
                if self.error_count < 2:
                    self.error_count += 1
                    raise RuntimeError("Simulated error")
                self.recovered = True

            def on_error(self, error: Exception):
                # Log error and continue
                pass

        strategy = RecoveryStrategy()

        # First two calls should error
        with pytest.raises(RuntimeError):
            strategy.on_market_data(MagicMock())

        with pytest.raises(RuntimeError):
            strategy.on_market_data(MagicMock())

        # Third call should succeed
        strategy.on_market_data(MagicMock())
        assert strategy.recovered
