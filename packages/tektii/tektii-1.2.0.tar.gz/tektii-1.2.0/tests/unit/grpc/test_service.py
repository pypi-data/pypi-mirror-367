"""Unit tests for gRPC service implementation."""

from __future__ import annotations

import threading
import time
from decimal import Decimal
from unittest.mock import ANY, MagicMock, Mock, patch

from tektii.strategy.base import TektiiStrategy
from tektii.strategy.grpc import orders_pb2
from tektii.strategy.grpc.service import TektiiStrategyService, serve
from tektii.strategy.models import BarData, TickData


class MockStrategy(TektiiStrategy):
    """Mock strategy for testing."""

    def __init__(self):
        super().__init__()
        self.events_received = []
        self.initialized = False
        self.shutdown = False
        self.errors = []
        self._lock = threading.Lock()  # For thread-safe operations

    def on_market_data(self, tick_data: TickData | None = None, bar_data: BarData | None = None) -> None:
        with self._lock:
            self.events_received.append(("market_data", tick_data, bar_data))

    def on_initialize(self, config: dict[str, str], symbols: list[str]) -> None:
        with self._lock:
            self.initialized = True
            self.events_received.append(("initialize", config, symbols))

    def on_shutdown(self) -> None:
        with self._lock:
            self.shutdown = True
            self.events_received.append(("shutdown",))

    def on_error(self, error: Exception) -> None:
        with self._lock:
            self.errors.append(error)


class TestTektiiStrategyService:
    """Test suite for TektiiStrategyService."""

    def test_service_initialization(self):
        """Test service initialization."""
        strategy = MockStrategy()
        service = TektiiStrategyService(strategy)

        assert service.strategy == strategy
        assert service._broker_address is None
        assert service._connection_manager is None
        assert isinstance(service._shutdown_event, threading.Event)
        assert not service._shutdown_event.is_set()

    def test_service_initialization_with_broker_address(self):
        """Test service initialization with broker address."""
        strategy = MockStrategy()
        broker_address = "localhost:50052"

        service = TektiiStrategyService(strategy, broker_address=broker_address)

        assert service._broker_address == broker_address
        assert service._connection_manager is None  # Connection manager created during Initialize
        assert not service._initialized

    def test_initialize_method(self):
        """Test Initialize RPC method."""
        strategy = MockStrategy()
        service = TektiiStrategyService(strategy)

        # Create initialization request
        request = orders_pb2.InitRequest()
        request.config["param1"] = "value1"
        request.config["param2"] = "value2"
        request.symbols.extend(["AAPL", "GOOGL", "MSFT"])

        # Call Initialize
        context = MagicMock()
        response = service.Initialize(request, context)

        assert isinstance(response, orders_pb2.InitResponse)
        assert response.success is True
        assert response.message == "Strategy initialized successfully"
        assert strategy.initialized is True

        # Check events
        assert len(strategy.events_received) == 1
        event = strategy.events_received[0]
        assert event[0] == "initialize"
        assert event[1] == {"param1": "value1", "param2": "value2"}
        assert event[2] == ["AAPL", "GOOGL", "MSFT"]

    def test_initialize_with_exception(self):
        """Test Initialize RPC with exception."""
        strategy = MockStrategy()
        strategy.on_initialize = Mock(side_effect=ValueError("Init failed"))
        service = TektiiStrategyService(strategy)

        request = orders_pb2.InitRequest()
        context = MagicMock()

        response = service.Initialize(request, context)

        assert response.success is False
        assert "Init failed" in response.message

    def test_send_event_tick_data(self):
        """Test ProcessEvent RPC with tick data."""
        strategy = MockStrategy()
        service = TektiiStrategyService(strategy)

        # Create tick data event
        request = orders_pb2.TektiiEvent()
        request.timestamp_us = 1234567890  # timestamp is on the event, not tick_data
        request.tick_data.symbol = "AAPL"
        request.tick_data.last = 150.50  # proto uses double, not string
        request.tick_data.bid = 150.49
        request.tick_data.ask = 150.51
        request.tick_data.last_size = 10000  # volume is last_size in proto

        # Call ProcessEvent
        context = MagicMock()
        response = service.ProcessEvent(request, context)

        assert isinstance(response, orders_pb2.ProcessEventResponse)
        assert response.success is True

        # Check event was processed
        assert len(strategy.events_received) == 1
        event = strategy.events_received[0]
        assert event[0] == "market_data"
        assert event[1] is not None  # tick_data
        assert event[1].symbol == "AAPL"
        assert float(event[1].last) == 150.50  # Compare as float since proto uses double
        assert event[2] is None  # bar_data

    def test_send_event_bar_data(self):
        """Test ProcessEvent RPC with bar data."""
        strategy = MockStrategy()
        service = TektiiStrategyService(strategy)

        # Create bar data event
        request = orders_pb2.TektiiEvent()
        request.timestamp_us = 1234567890  # timestamp is on the event
        request.bar_data.symbol = "GOOGL"
        request.bar_data.open = 2500.00  # proto uses double, not string
        request.bar_data.high = 2510.00
        request.bar_data.low = 2495.00
        request.bar_data.close = 2505.00
        request.bar_data.volume = 50000

        # Call ProcessEvent
        context = MagicMock()
        response = service.ProcessEvent(request, context)

        assert response.success is True

        # Check event was processed
        assert len(strategy.events_received) == 1
        event = strategy.events_received[0]
        assert event[0] == "market_data"
        assert event[1] is None  # tick_data
        assert event[2] is not None  # bar_data
        assert event[2].symbol == "GOOGL"
        assert event[2].close == Decimal("2505.00")

    def test_send_event_with_exception(self):
        """Test ProcessEvent RPC with exception in handler."""
        strategy = MockStrategy()
        strategy.on_market_data = Mock(side_effect=RuntimeError("Handler error"))
        service = TektiiStrategyService(strategy)

        # Create event
        request = orders_pb2.TektiiEvent()
        request.tick_data.symbol = "AAPL"
        request.tick_data.last = 150.00

        context = MagicMock()
        response = service.ProcessEvent(request, context)

        # Should still return success (errors are logged but not propagated)
        assert response.success is True

    def test_shutdown_method(self):
        """Test Shutdown RPC method."""
        strategy = MockStrategy()
        service = TektiiStrategyService(strategy)

        request = orders_pb2.ShutdownRequest()
        context = MagicMock()

        response = service.Shutdown(request, context)

        assert isinstance(response, orders_pb2.ShutdownResponse)
        assert response.success is True
        assert response.message == "Strategy shutdown successfully"
        assert service._shutdown_event.is_set()
        assert strategy.shutdown is True

    def test_shutdown_with_exception(self):
        """Test Shutdown RPC with exception."""
        strategy = MockStrategy()
        strategy.on_shutdown = Mock(side_effect=ValueError("Shutdown failed"))
        service = TektiiStrategyService(strategy)

        request = orders_pb2.ShutdownRequest()
        context = MagicMock()

        response = service.Shutdown(request, context)

        # Should still set shutdown event
        assert response.success is True
        assert service._shutdown_event.is_set()


class TestServeFunction:
    """Test suite for serve function."""

    @patch("grpc.server")
    @patch("tektii.strategy.grpc.service.health")
    @patch("tektii.strategy.grpc.service.TektiiStrategyService")
    def test_serve_basic(self, mock_service_class, mock_health, mock_grpc_server):
        """Test basic serve function."""
        # Set up mocks
        mock_server = MagicMock()
        mock_grpc_server.return_value = mock_server
        mock_health_servicer = MagicMock()
        mock_health.HealthServicer.return_value = mock_health_servicer

        # Mock the service instance to raise KeyboardInterrupt on wait_for_shutdown
        mock_service = MagicMock()
        mock_service.wait_for_shutdown.side_effect = KeyboardInterrupt
        mock_service_class.return_value = mock_service

        # Test with strategy class - should not raise because it's caught
        serve(MockStrategy, port=50051)

        # Verify server was set up
        mock_grpc_server.assert_called_once()
        assert mock_server.add_insecure_port.called
        assert mock_server.start.called
        assert mock_server.stop.called  # Should gracefully stop

    @patch("grpc.server")
    @patch("tektii.strategy.grpc.service.TektiiStrategyService")
    def test_serve_with_broker_address(self, mock_service_class, mock_grpc_server):
        """Test serve with broker address."""
        mock_server = MagicMock()
        mock_grpc_server.return_value = mock_server

        # Mock the service instance to raise KeyboardInterrupt on wait_for_shutdown
        mock_service = MagicMock()
        mock_service.wait_for_shutdown.side_effect = KeyboardInterrupt
        mock_service_class.return_value = mock_service

        # Test - should not raise because it's caught
        serve(MockStrategy, port=50051, broker_address="localhost:5555")

        # Verify service was created with broker address
        mock_service_class.assert_called_once_with(ANY, "localhost:5555")
        # Verify shutdown was called
        mock_service.shutdown.assert_called_once()


class TestServiceIntegration:
    """Integration tests for service functionality."""

    def test_service_lifecycle(self):
        """Test complete service lifecycle."""
        strategy = MockStrategy()
        service = TektiiStrategyService(strategy)

        # Initialize
        init_request = orders_pb2.InitRequest()
        init_request.config["test"] = "value"
        init_request.symbols.append("AAPL")

        context = MagicMock()
        init_response = service.Initialize(init_request, context)
        assert init_response.success is True

        # Send some events
        for i in range(5):
            event = orders_pb2.TektiiEvent()
            event.tick_data.symbol = "AAPL"
            event.tick_data.last = 150.0 + i

            response = service.ProcessEvent(event, context)
            assert response.success is True

        assert len(strategy.events_received) == 6  # 1 init + 5 market data

        # Shutdown
        shutdown_request = orders_pb2.ShutdownRequest()
        shutdown_response = service.Shutdown(shutdown_request, context)
        assert shutdown_response.success is True

        # Verify shutdown event is set
        assert service._shutdown_event.is_set()

    def test_concurrent_event_processing(self):
        """Test concurrent event processing."""
        strategy = MockStrategy()
        service = TektiiStrategyService(strategy)

        # Use threading to send concurrent events
        def send_events(symbol: str, count: int):
            context = MagicMock()
            for i in range(count):
                event = orders_pb2.TektiiEvent()
                event.tick_data.symbol = symbol
                event.tick_data.last = 100.0 + i
                service.ProcessEvent(event, context)

        threads = []
        symbols = ["AAPL", "GOOGL", "MSFT"]

        for symbol in symbols:
            t = threading.Thread(target=send_events, args=(symbol, 10))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # Should have received all events
        assert len(strategy.events_received) == 30  # 3 symbols * 10 events each

    def test_graceful_shutdown_with_pending_events(self):
        """Test graceful shutdown with pending events."""
        strategy = MockStrategy()
        service = TektiiStrategyService(strategy)

        # Add delay to market data processing
        original_method = strategy.on_market_data

        def slow_market_data(*args, **kwargs):
            time.sleep(0.1)
            original_method(*args, **kwargs)

        strategy.on_market_data = slow_market_data

        # Start sending events in background
        def send_many_events():
            context = MagicMock()
            for i in range(20):
                event = orders_pb2.TektiiEvent()
                event.tick_data.symbol = "AAPL"
                event.tick_data.last = 150.0 + i
                service.ProcessEvent(event, context)

        event_thread = threading.Thread(target=send_many_events)
        event_thread.start()

        # Give it a moment to start processing
        time.sleep(0.05)

        # Shutdown while events are being processed
        context = MagicMock()
        shutdown_request = orders_pb2.ShutdownRequest()
        shutdown_response = service.Shutdown(shutdown_request, context)

        assert shutdown_response.success is True
        assert service._shutdown_event.is_set()

        event_thread.join(timeout=3.0)
        assert not event_thread.is_alive()
