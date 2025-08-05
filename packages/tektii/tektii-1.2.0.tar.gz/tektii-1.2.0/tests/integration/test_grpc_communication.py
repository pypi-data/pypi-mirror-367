"""Integration tests for gRPC communication between strategy and broker."""

import time
from concurrent import futures
from typing import Any, Optional

import grpc
import pytest
from grpc_health.v1 import health, health_pb2, health_pb2_grpc

from tektii.strategy.base import TektiiStrategy
from tektii.strategy.grpc import common_pb2, orders_pb2, service_pb2_grpc
from tektii.strategy.models import OrderBuilder
from tektii.strategy.models.events import OrderUpdateEvent, TektiiEvent
from tektii.testing.mock_broker import MockBrokerService


class GRPCTestStrategy(TektiiStrategy):
    """Strategy for testing gRPC communication."""

    def __init__(self) -> None:
        super().__init__()
        self.events_received = []
        self.orders_sent = []
        self.errors_encountered = []

    def on_market_data(self, event: TektiiEvent) -> None:
        """Handle market data events."""
        self.events_received.append(("market_data", event))

        # Place an order on first tick
        if len(self.orders_sent) == 0 and event.tick_data:
            try:
                order = OrderBuilder().symbol(event.tick_data.symbol).buy().market().quantity(100).build()
                self.place_order(order)
                self.orders_sent.append(order)
            except Exception as e:
                self.errors_encountered.append(e)

    def on_order_update(self, event: OrderUpdateEvent) -> None:
        """Handle order update events."""
        self.events_received.append(("order_update", event))


class StrategyGRPCService(service_pb2_grpc.TektiiStrategyServicer):
    """gRPC service implementation for strategy testing."""

    def __init__(self, strategy: TektiiStrategy) -> None:
        self.strategy = strategy
        self.connected = False
        self.event_stream: Optional[Any] = None

    def ProcessEvent(self, request: orders_pb2.TektiiEvent, context: grpc.ServicerContext) -> orders_pb2.ProcessEventResponse:
        """Process a single event."""
        response = orders_pb2.ProcessEventResponse()

        try:
            # Dispatch event to strategy
            # This would require proper conversion from proto to model
            response.success = True
        except Exception as e:
            response.success = False
            response.error = str(e)

        return response

    def Initialize(self, request: orders_pb2.InitRequest, context: grpc.ServicerContext) -> orders_pb2.InitResponse:
        """Initialize the strategy."""
        response = orders_pb2.InitResponse()

        try:
            self.strategy._initialize(
                config=dict(request.config),
                symbols=list(request.symbols),
                strategy_id=request.strategy_id,
            )
            response.success = True
            response.message = "Strategy initialized"
        except Exception as e:
            response.success = False
            response.message = str(e)

        return response

    def Shutdown(self, request: orders_pb2.ShutdownRequest, context: grpc.ServicerContext) -> orders_pb2.ShutdownResponse:
        """Handle shutdown request."""
        response = orders_pb2.ShutdownResponse()

        try:
            self.strategy._shutdown()
            response.success = True
            response.message = "Strategy shutdown complete"
        except Exception as e:
            response.success = False
            response.message = str(e)

        return response


class TestGRPCCommunication:
    """Test gRPC communication between components."""

    @pytest.fixture
    def grpc_server(self) -> grpc.Server:
        """Create a gRPC server for testing."""
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        return server

    def test_broker_service_health_check(self) -> None:
        """Test broker service health check."""
        # Start mock broker server
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        broker = MockBrokerService()
        service_pb2_grpc.add_TektiiBrokerServicer_to_server(broker, server)

        # Add health service
        health_servicer = health.HealthServicer()
        health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)
        health_servicer.set("", health_pb2.HealthCheckResponse.SERVING)
        health_servicer.set("tektii.broker", health_pb2.HealthCheckResponse.SERVING)

        port = server.add_insecure_port("[::]:0")
        server.start()

        try:
            # Create client channel
            channel = grpc.insecure_channel(f"localhost:{port}")
            health_stub = health_pb2_grpc.HealthStub(channel)

            # Check overall health
            request = health_pb2.HealthCheckRequest()
            response = health_stub.Check(request)
            assert response.status == health_pb2.HealthCheckResponse.SERVING

            # Check service-specific health
            request = health_pb2.HealthCheckRequest(service="tektii.broker")
            response = health_stub.Check(request)
            assert response.status == health_pb2.HealthCheckResponse.SERVING

        finally:
            server.stop(grace=0)

    def test_strategy_service_health_check(self) -> None:
        """Test strategy service health check."""
        # Create strategy and server
        strategy = GRPCTestStrategy()
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

        # Add strategy service
        strategy_service = StrategyGRPCService(strategy)
        service_pb2_grpc.add_TektiiStrategyServicer_to_server(strategy_service, server)

        # Add health service
        health_servicer = health.HealthServicer()
        health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)
        health_servicer.set("", health_pb2.HealthCheckResponse.SERVING)
        health_servicer.set("tektii.strategy", health_pb2.HealthCheckResponse.SERVING)

        port = server.add_insecure_port("[::]:0")
        server.start()

        try:
            # Create client channel
            channel = grpc.insecure_channel(f"localhost:{port}")
            health_stub = health_pb2_grpc.HealthStub(channel)

            # Check health
            request = health_pb2.HealthCheckRequest(service="tektii.strategy")
            response = health_stub.Check(request)
            assert response.status == health_pb2.HealthCheckResponse.SERVING

        finally:
            server.stop(grace=0)

    def test_strategy_initialization(self) -> None:
        """Test strategy initialization via gRPC."""
        # Create strategy and server
        strategy = GRPCTestStrategy()

        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        strategy_service = StrategyGRPCService(strategy)
        service_pb2_grpc.add_TektiiStrategyServicer_to_server(strategy_service, server)

        port = server.add_insecure_port("[::]:0")
        server.start()

        try:
            # Create client
            channel = grpc.insecure_channel(f"localhost:{port}")
            stub = service_pb2_grpc.TektiiStrategyStub(channel)

            # Initialize strategy
            request = orders_pb2.InitRequest(
                config={"test_mode": "true"},
                symbols=["AAPL", "GOOGL"],
                strategy_id="test-123",
            )
            response = stub.Initialize(request)

            assert response.success
            assert "initialized" in response.message

        finally:
            server.stop(grace=0)

    def test_strategy_shutdown(self) -> None:
        """Test strategy shutdown via gRPC."""
        # Create strategy and server
        strategy = GRPCTestStrategy()
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        strategy_service = StrategyGRPCService(strategy)
        service_pb2_grpc.add_TektiiStrategyServicer_to_server(strategy_service, server)

        port = server.add_insecure_port("[::]:0")
        server.start()

        try:
            # Create client
            channel = grpc.insecure_channel(f"localhost:{port}")
            stub = service_pb2_grpc.TektiiStrategyStub(channel)

            # Send shutdown request
            request = orders_pb2.ShutdownRequest(
                reason="Test shutdown",
                force=False,
            )
            response = stub.Shutdown(request)

            assert response.success
            assert "shutdown complete" in response.message

        finally:
            server.stop(grace=0)

    def test_channel_connectivity(self) -> None:
        """Test gRPC channel connectivity states."""
        # Start a server
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        broker = MockBrokerService()
        service_pb2_grpc.add_TektiiBrokerServicer_to_server(broker, server)
        port = server.add_insecure_port("[::]:0")
        server.start()

        try:
            # Create channel
            channel = grpc.insecure_channel(f"localhost:{port}")

            # Check initial state
            state = channel._channel.check_connectivity_state(True)
            # State is represented as an integer, not the enum
            assert state in [0, 1, 2]  # IDLE=0, CONNECTING=1, READY=2

            # Make a call to establish connection
            stub = service_pb2_grpc.TektiiBrokerStub(channel)
            request = orders_pb2.ValidateOrderRequest(
                symbol="TEST",
                side=common_pb2.ORDER_SIDE_BUY,
                order_type=common_pb2.ORDER_TYPE_MARKET,
                quantity=100.0,
            )
            response = stub.ValidateOrder(request)
            assert response.valid

            # Check connected state
            state = channel._channel.check_connectivity_state(False)
            assert state == 2  # READY=2

        finally:
            server.stop(grace=0)

    def test_error_propagation(self) -> None:
        """Test error propagation through gRPC."""

        # Create a broker that will return errors
        class ErrorBroker(MockBrokerService):
            def PlaceOrder(self, request: Any, context: grpc.ServicerContext) -> Any:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Test error: Invalid order")
                raise ValueError("Test error")

        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        broker = ErrorBroker()
        service_pb2_grpc.add_TektiiBrokerServicer_to_server(broker, server)
        port = server.add_insecure_port("[::]:0")
        server.start()

        try:
            # Create client
            channel = grpc.insecure_channel(f"localhost:{port}")
            stub = service_pb2_grpc.TektiiBrokerStub(channel)

            # Try to place order
            request = orders_pb2.PlaceOrderRequest(
                symbol="TEST",
                side=common_pb2.ORDER_SIDE_BUY,
                order_type=common_pb2.ORDER_TYPE_MARKET,
                quantity=100.0,
            )

            with pytest.raises(grpc.RpcError) as exc_info:
                stub.PlaceOrder(request)

            assert exc_info.value.code() == grpc.StatusCode.INVALID_ARGUMENT
            assert "Test error" in exc_info.value.details()

        finally:
            server.stop(grace=0)

    def test_deadline_handling(self) -> None:
        """Test gRPC deadline/timeout handling."""

        # Create a slow broker
        class SlowBroker(MockBrokerService):
            def GetState(self, request: Any, context: grpc.ServicerContext) -> Any:
                time.sleep(2)  # Simulate slow response
                return super().GetState(request, context)

        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        broker = SlowBroker()
        service_pb2_grpc.add_TektiiBrokerServicer_to_server(broker, server)
        port = server.add_insecure_port("[::]:0")
        server.start()

        try:
            # Create client with short timeout
            channel = grpc.insecure_channel(f"localhost:{port}")
            stub = service_pb2_grpc.TektiiBrokerStub(channel)

            # Try to get state with timeout
            request = orders_pb2.StateRequest(include_positions=True)

            with pytest.raises(grpc.RpcError) as exc_info:
                stub.GetState(request, timeout=0.5)  # 500ms timeout

            assert exc_info.value.code() == grpc.StatusCode.DEADLINE_EXCEEDED

        finally:
            server.stop(grace=0)

    @pytest.mark.skip(reason="Requires full bidirectional streaming implementation")
    def test_bidirectional_streaming(self) -> None:
        """Test bidirectional streaming between strategy and broker."""
        # This test would require full implementation of the Connect RPC
        # with proper event streaming in both directions
        pass

    def test_concurrent_requests(self) -> None:
        """Test handling concurrent gRPC requests."""
        from concurrent import futures as cf

        server = grpc.server(cf.ThreadPoolExecutor(max_workers=10))
        broker = MockBrokerService()
        service_pb2_grpc.add_TektiiBrokerServicer_to_server(broker, server)
        port = server.add_insecure_port("[::]:0")
        server.start()

        try:
            # Create multiple clients
            channels = []
            stubs = []
            for _ in range(5):
                channel = grpc.insecure_channel(f"localhost:{port}")
                channels.append(channel)
                stubs.append(service_pb2_grpc.TektiiBrokerStub(channel))

            # Send concurrent requests
            def place_order(stub: Any, i: int) -> Any:
                request = orders_pb2.PlaceOrderRequest(
                    symbol=f"TEST{i}",
                    side=common_pb2.ORDER_SIDE_BUY,
                    order_type=common_pb2.ORDER_TYPE_MARKET,
                    quantity=100.0 + i,
                    request_id=f"req-{i:03d}",
                )
                return stub.PlaceOrder(request)

            # Execute requests concurrently
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [executor.submit(place_order, stub, i) for i, stub in enumerate(stubs)]
                responses = [f.result() for f in futures]

            # Verify all succeeded
            assert len(responses) == 5
            for i, response in enumerate(responses):
                assert response.accepted
                assert response.request_id == f"req-{i:03d}"

            # Verify all orders were created
            assert len(broker.orders) == 5

        finally:
            server.stop(grace=0)
            for channel in channels:
                channel.close()
