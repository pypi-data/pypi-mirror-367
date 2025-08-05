"""Test harness for running strategies with a mock broker.

This module provides utilities for testing strategies in a controlled
environment with a mock broker implementation.
"""

from __future__ import annotations

import time
from concurrent import futures
from typing import Any, Callable, Dict, Optional, Type

import grpc
from grpc_health.v1 import health, health_pb2, health_pb2_grpc

from tektii.strategy.base import TektiiStrategy

# orders_pb2_grpc not generated yet
from tektii.strategy.grpc import common_pb2, service_pb2_grpc
from tektii.testing.mock_broker import MockBrokerService


class StrategyTestHarness:
    """Test harness for running strategies with a mock broker."""

    def __init__(self, strategy_class: Type[TektiiStrategy]) -> None:
        """Initialize the test harness.

        Args:
            strategy_class: The strategy class to test.
        """
        self.strategy_class = strategy_class
        self.strategy: Optional[TektiiStrategy] = None
        self.mock_broker = MockBrokerService()
        self.broker_server: Optional[grpc.Server] = None
        self.broker_channel: Optional[grpc.Channel] = None
        self.broker_port = 50052

    def start(self) -> None:
        """Start the test harness with mock broker."""
        # Configure server with keepalive settings to match client expectations
        server_options = [
            ("grpc.keepalive_time_ms", 10000),  # Send keepalive every 10 seconds
            ("grpc.keepalive_timeout_ms", 5000),  # Timeout after 5 seconds
            ("grpc.keepalive_permit_without_calls", True),
            ("grpc.http2.max_pings_without_data", 0),
            ("grpc.http2.min_recv_ping_interval_without_data_ms", 5000),
            ("grpc.http2.min_sent_ping_interval_without_data_ms", 10000),
        ]

        # Start mock broker server with keepalive options
        self.broker_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10), options=server_options)
        service_pb2_grpc.add_TektiiBrokerServicer_to_server(self.mock_broker, self.broker_server)  # type: ignore[no-untyped-call]

        # Add health check service
        health_servicer = health.HealthServicer()
        health_pb2_grpc.add_HealthServicer_to_server(health_servicer, self.broker_server)
        # Set the broker service as SERVING
        health_servicer.set("", health_pb2.HealthCheckResponse.SERVING)
        health_servicer.set("tektii.broker", health_pb2.HealthCheckResponse.SERVING)

        self.broker_server.add_insecure_port(f"[::]:{self.broker_port}")
        self.broker_server.start()

        # Create broker channel with matching keepalive settings
        channel_options = [
            ("grpc.keepalive_time_ms", 10000),
            ("grpc.keepalive_timeout_ms", 5000),
            ("grpc.keepalive_permit_without_calls", True),
            ("grpc.http2.max_pings_without_data", 0),
        ]
        self.broker_channel = grpc.insecure_channel(f"localhost:{self.broker_port}", options=channel_options)

        # Create strategy instance with broker channel
        self.strategy = self.strategy_class()
        # Note: Will create proper stub once proto is generated
        self.strategy._set_broker_stub(self.broker_channel)

        # Initialize strategy
        config = {"test_mode": "true"}
        symbols = ["TEST"]
        self.strategy._initialize(config, symbols, "test-strategy")

    def stop(self) -> None:
        """Stop the test harness and clean up resources."""
        if self.strategy:
            self.strategy._shutdown()

        if self.broker_channel:
            self.broker_channel.close()

        if self.broker_server:
            self.broker_server.stop(grace=0)

    def send_event(self, event: Any) -> None:
        """Send an event to the strategy.

        Args:
            event: The event to send.
        """
        if not self.strategy:
            raise RuntimeError("Harness not started")

        # For testing, we need to convert the event to a TektiiEvent
        # This would typically be done by the test code
        if hasattr(event, "to_proto"):
            proto_event = event.to_proto()
            self.strategy._handle_event(proto_event)
        else:
            raise ValueError("Event must be a proto message or have to_proto method")

    def place_test_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        order_type: str = "MARKET",
        limit_price: float = 0.0,
    ) -> Dict[str, Any]:
        """Place a test order directly through the broker.

        Args:
            symbol: Symbol to trade.
            side: Order side (BUY/SELL).
            quantity: Order quantity.
            order_type: Order type (MARKET/LIMIT).
            limit_price: Limit price for limit orders.

        Returns:
            Order placement result.
        """
        if not self.strategy:
            raise RuntimeError("Harness not started")

        # Would create PlaceOrderRequest from proto once generated
        _ = {
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "order_type": order_type,
            "limit_price": limit_price,
        }

        # Simplified for now - would use broker stub
        return {"order_id": "test-order", "status": "submitted"}

    def get_positions(self) -> Dict[str, Any]:
        """Get current positions from the mock broker.

        Returns:
            Dictionary of positions by symbol.
        """
        if not self.strategy:
            raise RuntimeError("Harness not started")

        # Simplified for now - would use query_state once implemented
        return self.strategy._positions if hasattr(self.strategy, "_positions") else {}

    def get_orders(self) -> Dict[str, Any]:
        """Get current orders from the mock broker.

        Returns:
            Dictionary of orders by order ID.
        """
        if not self.strategy:
            raise RuntimeError("Harness not started")

        # Simplified for now - would use query_state once implemented
        return self.strategy._orders if hasattr(self.strategy, "_orders") else {}

    def get_account(self) -> Dict[str, Any]:
        """Get account information from the mock broker.

        Returns:
            Account state.
        """
        if not self.strategy:
            raise RuntimeError("Harness not started")

        # Simplified for now - would use query_state once implemented
        return {"cash_balance": 100000.0, "portfolio_value": 100000.0}

    def set_account_balance(self, cash_balance: float) -> None:
        """Set the mock account balance.

        Args:
            cash_balance: New cash balance.
        """
        self.mock_broker.account.cash_balance = cash_balance
        self.mock_broker.account.portfolio_value = cash_balance
        self.mock_broker.account.buying_power = cash_balance

    def simulate_order_fill(self, order_id: str, fill_price: float) -> None:
        """Simulate filling an order.

        Args:
            order_id: Order ID to fill.
            fill_price: Fill price.
        """
        if order_id in self.mock_broker.orders:
            order = self.mock_broker.orders[order_id]
            order.status = common_pb2.ORDER_STATUS_FILLED
            order.filled_quantity = order.quantity

            # Update position
            if order.symbol not in self.mock_broker.positions:
                self.mock_broker.positions[order.symbol] = common_pb2.Position(
                    symbol=order.symbol,
                    quantity=0.0,
                    avg_price=0.0,
                    market_value=0.0,
                    unrealized_pnl=0.0,
                    realized_pnl=0.0,
                    current_price=fill_price,
                )

            position = self.mock_broker.positions[order.symbol]
            if order.side == common_pb2.ORDER_SIDE_BUY:
                position.quantity += order.quantity
            else:
                position.quantity -= order.quantity

            position.avg_price = fill_price
            position.market_value = position.quantity * fill_price

    def wait(self, seconds: float) -> None:
        """Wait for a specified duration.

        Args:
            seconds: Number of seconds to wait.
        """
        time.sleep(seconds)


def run_strategy_test(
    strategy_class: Type[TektiiStrategy],
    test_function: Callable[[StrategyTestHarness], None],
    setup_function: Optional[Callable[[StrategyTestHarness], None]] = None,
    teardown_function: Optional[Callable[[StrategyTestHarness], None]] = None,
) -> None:
    """Run a strategy test with automatic setup and teardown.

    Args:
        strategy_class: The strategy class to test.
        test_function: Test function that receives the harness.
        setup_function: Optional setup function.
        teardown_function: Optional teardown function.
    """
    harness = StrategyTestHarness(strategy_class)

    try:
        harness.start()

        if setup_function:
            setup_function(harness)

        test_function(harness)

        if teardown_function:
            teardown_function(harness)

    finally:
        harness.stop()
