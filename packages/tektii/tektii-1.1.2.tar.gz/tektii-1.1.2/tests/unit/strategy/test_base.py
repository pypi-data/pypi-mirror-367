"""Unit tests for TektiiStrategy base class."""

from __future__ import annotations

from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from tektii.strategy.base import TektiiStrategy
from tektii.strategy.grpc import orders_pb2
from tektii.strategy.models import (
    AccountUpdateEvent,
    BarData,
    Order,
    OrderSide,
    OrderStatus,
    OrderType,
    OrderUpdateEvent,
    PositionUpdateEvent,
    SystemEvent,
    SystemEventType,
    TickData,
    TradeEvent,
)


class ConcreteStrategy(TektiiStrategy):
    """Concrete implementation of TektiiStrategy for testing."""

    def __init__(self):
        super().__init__()
        self.market_data_calls = []
        self.order_update_calls = []
        self.position_update_calls = []
        self.account_update_calls = []
        self.trade_calls = []
        self.system_event_calls = []
        self.initialize_calls = []
        self.shutdown_calls = []

    def on_market_data(self, tick_data: TickData | None = None, bar_data: BarData | None = None) -> None:
        self.market_data_calls.append({"tick_data": tick_data, "bar_data": bar_data})

    def on_order_update(self, order_update: OrderUpdateEvent) -> None:
        self.order_update_calls.append(order_update)
        # Update internal order tracking
        order = Order(
            order_id=order_update.order_id,
            symbol=order_update.symbol,
            status=order_update.status,
            side=order_update.side,
            order_type=order_update.order_type,
            quantity=order_update.quantity,
            filled_quantity=order_update.filled_quantity,
            limit_price=order_update.limit_price,
            stop_price=order_update.stop_price,
            created_at_us=order_update.created_at_us,
        )
        self._orders[order_update.order_id] = order

    def on_position_update(self, position_update: PositionUpdateEvent) -> None:
        self.position_update_calls.append(position_update)

    def on_account_update(self, account_update: AccountUpdateEvent) -> None:
        self.account_update_calls.append(account_update)

    def on_trade(self, trade: TradeEvent) -> None:
        self.trade_calls.append(trade)

    def on_system_event(self, system_event: SystemEvent) -> None:
        self.system_event_calls.append(system_event)

    def on_initialize(self, config: dict[str, str], symbols: list[str]) -> None:
        self.initialize_calls.append({"config": config, "symbols": symbols})

    def on_shutdown(self) -> None:
        self.shutdown_calls.append(True)


class TestTektiiStrategyBase:
    """Test suite for TektiiStrategy base class."""

    def test_strategy_is_abstract(self):
        """Test that TektiiStrategy cannot be instantiated directly."""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            TektiiStrategy()  # type: ignore

    def test_concrete_strategy_initialization(self):
        """Test that concrete strategies can be initialized."""
        strategy = ConcreteStrategy()
        assert strategy is not None
        assert hasattr(strategy, "_positions")
        assert hasattr(strategy, "_orders")
        assert hasattr(strategy, "_account")
        assert strategy._positions == {}
        assert strategy._orders == {}
        assert strategy._account is None

    def test_handle_tick_data_event(self):
        """Test handling of tick data events."""
        strategy = ConcreteStrategy()

        # Create a tick data proto event
        event = orders_pb2.TektiiEvent()
        event.timestamp_us = 1234567890  # Event timestamp
        event.tick_data.symbol = "AAPL"
        event.tick_data.last = 150.50
        event.tick_data.bid = 150.49
        event.tick_data.ask = 150.51
        event.tick_data.last_size = 100
        event.tick_data.bid_size = 500
        event.tick_data.ask_size = 300

        strategy._handle_event(event)

        assert len(strategy.market_data_calls) == 1
        call = strategy.market_data_calls[0]
        assert call["tick_data"] is not None
        assert call["bar_data"] is None
        assert call["tick_data"].symbol == "AAPL"
        assert call["tick_data"].last == Decimal("150.50")
        assert call["tick_data"].bid == Decimal("150.49")
        assert call["tick_data"].ask == Decimal("150.51")

    def test_handle_bar_data_event(self):
        """Test handling of bar data events."""
        strategy = ConcreteStrategy()

        # Create a bar data proto event
        event = orders_pb2.TektiiEvent()
        event.timestamp_us = 1234567890  # Event timestamp
        event.bar_data.symbol = "GOOGL"
        event.bar_data.open = 2500.00
        event.bar_data.high = 2510.00
        event.bar_data.low = 2495.00
        event.bar_data.close = 2505.00
        event.bar_data.volume = 50000
        event.bar_data.bar_size = 5
        event.bar_data.bar_size_unit = "min"

        strategy._handle_event(event)

        assert len(strategy.market_data_calls) == 1
        call = strategy.market_data_calls[0]
        assert call["tick_data"] is None
        assert call["bar_data"] is not None
        assert call["bar_data"].symbol == "GOOGL"
        assert call["bar_data"].open == Decimal("2500.00")
        assert call["bar_data"].high == Decimal("2510.00")
        assert call["bar_data"].low == Decimal("2495.00")
        assert call["bar_data"].close == Decimal("2505.00")

    def test_handle_order_update_event(self):
        """Test handling of order update events."""
        strategy = ConcreteStrategy()

        # Create an order update proto event
        event = orders_pb2.TektiiEvent()
        event.timestamp_us = 1234567890
        event.order_update.order_id = "order123"
        event.order_update.symbol = "AAPL"
        event.order_update.side = OrderSide.BUY.to_proto()
        event.order_update.order_type = OrderType.LIMIT.to_proto()
        event.order_update.quantity = 100.0
        event.order_update.limit_price = 150.00
        event.order_update.status = OrderStatus.FILLED.to_proto()
        event.order_update.filled_quantity = 100.0
        event.order_update.created_at_us = 1234567890
        event.order_update.updated_at_us = 1234567890

        strategy._handle_event(event)

        assert len(strategy.order_update_calls) == 1
        update = strategy.order_update_calls[0]
        assert update.order_id == "order123"
        assert update.symbol == "AAPL"
        assert update.side == OrderSide.BUY
        assert update.status == OrderStatus.FILLED

        # Check internal order tracking
        assert "order123" in strategy._orders
        assert strategy._orders["order123"].status == OrderStatus.FILLED

    def test_handle_position_update_event(self):
        """Test handling of position update events."""
        strategy = ConcreteStrategy()

        # Create a position update proto event
        event = orders_pb2.TektiiEvent()
        event.timestamp_us = 1234567890
        event.position_update.symbol = "MSFT"
        event.position_update.quantity = 200.0
        event.position_update.avg_price = 300.00
        event.position_update.unrealized_pnl = 1000.00
        event.position_update.realized_pnl = 100.00
        event.position_update.market_value = 61000.00
        event.position_update.current_price = 305.00
        event.position_update.bid = 304.90
        event.position_update.ask = 305.10

        strategy._handle_event(event)

        assert len(strategy.position_update_calls) == 1
        update = strategy.position_update_calls[0]
        assert update.symbol == "MSFT"
        assert update.quantity == Decimal("200.0")
        assert update.avg_price == Decimal("300.00")
        assert update.unrealized_pnl == Decimal("1000.00")
        assert update.realized_pnl == Decimal("100.00")

        # Check internal position tracking
        assert "MSFT" in strategy._positions
        assert strategy._positions["MSFT"].quantity == Decimal("200.0")

    def test_handle_account_update_event(self):
        """Test handling of account update events."""
        strategy = ConcreteStrategy()

        # Create an account update proto event
        event = orders_pb2.TektiiEvent()
        event.timestamp_us = 1234567890
        event.account_update.cash_balance = 100000.00
        event.account_update.portfolio_value = 250000.00
        event.account_update.buying_power = 200000.00
        event.account_update.initial_margin = 50000.00
        event.account_update.maintenance_margin = 25000.00
        event.account_update.margin_used = 30000.00
        event.account_update.daily_pnl = 5000.00
        event.account_update.total_pnl = 15000.00
        event.account_update.leverage = 2.5

        strategy._handle_event(event)

        assert len(strategy.account_update_calls) == 1
        update = strategy.account_update_calls[0]
        assert update.cash_balance == Decimal("100000.00")
        assert update.buying_power == Decimal("200000.00")
        assert update.portfolio_value == Decimal("250000.00")
        assert update.daily_pnl == Decimal("5000.00")

        # Check internal account tracking
        assert strategy._account is not None
        assert strategy._account.cash_balance == Decimal("100000.00")

    def test_handle_trade_event(self):
        """Test handling of trade events."""
        strategy = ConcreteStrategy()

        # Create a trade proto event
        event = orders_pb2.TektiiEvent()
        event.timestamp_us = 1234567890
        event.trade.trade_id = "trade123"
        event.trade.order_id = "order123"
        event.trade.symbol = "AAPL"
        event.trade.side = OrderSide.BUY.to_proto()
        event.trade.price = 150.50
        event.trade.quantity = 50.0
        event.trade.timestamp_us = 1234567890
        event.trade.commission = 1.00
        event.trade.fees = 0.50

        strategy._handle_event(event)

        assert len(strategy.trade_calls) == 1
        trade = strategy.trade_calls[0]
        assert trade.trade_id == "trade123"
        assert trade.order_id == "order123"
        assert trade.symbol == "AAPL"
        assert trade.side == OrderSide.BUY
        assert trade.price == Decimal("150.50")
        assert trade.quantity == Decimal("50.0")
        assert trade.commission == Decimal("1.00")
        assert trade.fees == Decimal("0.50")

    def test_handle_system_event(self):
        """Test handling of system events."""
        strategy = ConcreteStrategy()

        # Create a system proto event
        event = orders_pb2.TektiiEvent()
        event.timestamp_us = 1234567890
        event.system.type = SystemEventType.CONNECTED.to_proto()
        event.system.message = "Connected to broker"

        strategy._handle_event(event)

        assert len(strategy.system_event_calls) == 1
        system_event = strategy.system_event_calls[0]
        assert system_event.type == SystemEventType.CONNECTED
        assert system_event.message == "Connected to broker"

    def test_handle_event_with_exception(self):
        """Test that exceptions in event handlers are logged but don't crash."""
        strategy = ConcreteStrategy()

        # Make on_market_data raise an exception
        def raise_error(*args, **kwargs):
            raise ValueError("Test error")

        strategy.on_market_data = raise_error  # type: ignore

        # Create a tick data event
        event = orders_pb2.TektiiEvent()
        event.timestamp_us = 1234567890
        event.tick_data.symbol = "AAPL"
        event.tick_data.last = 150.00

        # Should not raise exception
        with patch("tektii.strategy.base.logger") as mock_logger:
            strategy._handle_event(event)
            mock_logger.error.assert_called_once()
            assert "Error handling event" in str(mock_logger.error.call_args)

    def test_handle_unknown_event_type(self):
        """Test handling of unknown event types."""
        strategy = ConcreteStrategy()

        # Create an empty event (no field set)
        event = orders_pb2.TektiiEvent()

        # Should not raise exception or call any handlers
        strategy._handle_event(event)

        assert len(strategy.market_data_calls) == 0
        assert len(strategy.order_update_calls) == 0
        assert len(strategy.position_update_calls) == 0

    def test_lifecycle_methods(self):
        """Test strategy lifecycle methods."""
        strategy = ConcreteStrategy()

        # Test initialization
        config = {"param1": "value1", "param2": "value2"}
        symbols = ["AAPL", "GOOGL", "MSFT"]
        strategy.on_initialize(config, symbols)

        assert len(strategy.initialize_calls) == 1
        assert strategy.initialize_calls[0]["config"] == config
        assert strategy.initialize_calls[0]["symbols"] == symbols

        # Test shutdown
        strategy.on_shutdown()
        assert len(strategy.shutdown_calls) == 1
        assert strategy.shutdown_calls[0] is True

    def test_optional_methods_have_defaults(self):
        """Test that optional methods have no-op defaults."""

        class MinimalStrategy(TektiiStrategy):
            """Minimal strategy implementation."""

            def on_market_data(self, tick_data: TickData | None = None, bar_data: BarData | None = None) -> None:
                pass

        strategy = MinimalStrategy()

        # These should not raise exceptions
        strategy.on_order_update(MagicMock())
        strategy.on_position_update(MagicMock())
        strategy.on_account_update(MagicMock())
        strategy.on_trade(MagicMock())
        strategy.on_system_event(MagicMock())
        strategy.on_initialize({}, [])
        strategy.on_shutdown()

    def test_position_and_order_removal(self):
        """Test that closed orders and zero positions are removed from tracking."""
        strategy = ConcreteStrategy()

        # Add an order and track it
        event = orders_pb2.TektiiEvent()
        event.timestamp_us = 1234567890
        event.order_update.order_id = "order123"
        event.order_update.status = OrderStatus.PENDING.to_proto()
        event.order_update.symbol = "AAPL"
        event.order_update.side = OrderSide.BUY.to_proto()
        event.order_update.order_type = OrderType.LIMIT.to_proto()
        event.order_update.quantity = 100.0
        event.order_update.limit_price = 150.0
        event.order_update.filled_quantity = 0.0
        event.order_update.created_at_us = 1234567890

        strategy._handle_event(event)
        assert "order123" in strategy._orders  # Order is tracked

        # Add a position
        event = orders_pb2.TektiiEvent()
        event.timestamp_us = 1234567891
        event.position_update.symbol = "AAPL"
        event.position_update.quantity = 100.0
        event.position_update.avg_price = 150.0
        event.position_update.unrealized_pnl = 0.0
        event.position_update.realized_pnl = 0.0
        event.position_update.market_value = 15000.0
        event.position_update.current_price = 150.0

        strategy._handle_event(event)
        assert "AAPL" in strategy._positions

        # Update position to zero quantity
        event = orders_pb2.TektiiEvent()
        event.timestamp_us = 1234567892
        event.position_update.symbol = "AAPL"
        event.position_update.quantity = 0.0
        event.position_update.avg_price = 0.0
        event.position_update.unrealized_pnl = 0.0
        event.position_update.realized_pnl = 500.0
        event.position_update.market_value = 0.0
        event.position_update.current_price = 151.0

        strategy._handle_event(event)
        assert "AAPL" not in strategy._positions  # Zero positions are removed
