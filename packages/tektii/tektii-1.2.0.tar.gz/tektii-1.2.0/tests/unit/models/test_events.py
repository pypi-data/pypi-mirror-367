"""Unit tests for event models."""

from datetime import datetime
from decimal import Decimal

from tektii.strategy.models.enums import OrderSide, OrderStatus, OrderType
from tests.assertions import assert_decimal_equal
from tests.factories import AccountUpdateEventFactory, OrderUpdateEventFactory, PositionUpdateEventFactory


class TestOrderUpdateEvent:
    """Test OrderUpdateEvent model functionality."""

    def test_order_update_event_creation(self):
        """Test creating order update event."""
        event = OrderUpdateEventFactory()

        assert event.order_id is not None
        assert event.created_at_us > 0
        assert isinstance(event.created_at, datetime)

    def test_order_update_event_with_pending_order(self):
        """Test order update event for pending order."""
        event = OrderUpdateEventFactory(
            symbol="AAPL",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("100"),
            filled_quantity=Decimal("0"),
            status=OrderStatus.PENDING,
        )

        assert event.symbol == "AAPL"
        assert event.status == OrderStatus.PENDING
        assert event.filled_quantity == Decimal("0")

    def test_order_update_event_fill_event(self):
        """Test order update event for filled order."""
        event = OrderUpdateEventFactory(
            symbol="GOOGL",
            side=OrderSide.SELL,
            quantity=Decimal("50"),
            order_type=OrderType.MARKET,
            status=OrderStatus.FILLED,
            filled_quantity=Decimal("50"),
            avg_fill_price=Decimal("2500.75"),
        )

        assert event.status == OrderStatus.FILLED
        assert event.filled_quantity == Decimal("50")
        assert_decimal_equal(event.avg_fill_price, Decimal("2500.75"))

    def test_order_update_event_partial_fill(self):
        """Test order update event for partial fill."""
        event = OrderUpdateEventFactory(
            quantity=Decimal("100"), filled_quantity=Decimal("40"), status=OrderStatus.PARTIAL, avg_fill_price=Decimal("150.25")
        )

        assert event.status == OrderStatus.PARTIAL
        assert event.filled_quantity == Decimal("40")
        assert event.remaining_quantity == Decimal("60")

    def test_order_update_event_rejection(self):
        """Test order update event for rejected order."""
        event = OrderUpdateEventFactory(status=OrderStatus.REJECTED, filled_quantity=Decimal("0"), reject_reason="Insufficient buying power")

        assert event.status == OrderStatus.REJECTED
        assert not event.is_active
        assert event.filled_quantity == Decimal("0")
        assert event.reject_reason == "Insufficient buying power"

    def test_order_update_event_cancellation(self):
        """Test order update event for cancelled order."""
        event = OrderUpdateEventFactory(quantity=Decimal("100"), filled_quantity=Decimal("30"), status=OrderStatus.CANCELED)

        assert event.status == OrderStatus.CANCELED
        assert not event.is_active
        assert event.filled_quantity == Decimal("30")
        assert event.remaining_quantity == Decimal("70")


class TestPositionUpdateEvent:
    """Test PositionUpdateEvent model functionality."""

    def test_position_update_event_creation(self):
        """Test creating position update event."""
        event = PositionUpdateEventFactory()

        assert event.symbol is not None
        assert event.quantity is not None
        assert event.avg_price is not None

    def test_position_update_event_position_opened(self):
        """Test position update event for new position."""
        event = PositionUpdateEventFactory(symbol="AAPL", quantity=Decimal("100"), avg_price=Decimal("150.50"), current_price=Decimal("151.00"))

        assert event.symbol == "AAPL"
        assert event.quantity == Decimal("100")
        assert event.is_long
        assert_decimal_equal(event.avg_price, Decimal("150.50"))

    def test_position_update_event_position_closed(self):
        """Test position update event for closed position."""
        event = PositionUpdateEventFactory(symbol="GOOGL", quantity=Decimal("0"), realized_pnl=Decimal("250.75"), unrealized_pnl=Decimal("0"))

        assert event.symbol == "GOOGL"
        assert event.quantity == Decimal("0")
        assert event.is_flat
        assert_decimal_equal(event.realized_pnl, Decimal("250.75"))
        assert event.unrealized_pnl == Decimal("0")

    def test_position_update_event_position_increased(self):
        """Test position update event for increased position."""
        event = PositionUpdateEventFactory(
            symbol="MSFT",
            quantity=Decimal("200"),  # Increased from 100
            avg_price=Decimal("352.25"),  # New average after increase
            unrealized_pnl=Decimal("150.00"),
        )

        assert event.quantity == Decimal("200")
        assert event.is_long

    def test_position_update_event_position_reduced(self):
        """Test position update event for reduced position."""
        event = PositionUpdateEventFactory(
            symbol="SPY",
            quantity=Decimal("50"),  # Reduced from 100
            avg_price=Decimal("450.00"),
            realized_pnl=Decimal("100.00"),  # Realized some profit
            unrealized_pnl=Decimal("50.00"),
        )

        assert event.quantity == Decimal("50")
        assert_decimal_equal(event.realized_pnl, Decimal("100.00"))

    def test_position_update_event_short_position(self):
        """Test position update event for short position."""
        event = PositionUpdateEventFactory(symbol="TSLA", quantity=Decimal("-50"), avg_price=Decimal("800.00"))

        assert event.is_short
        assert event.quantity == Decimal("-50")


class TestAccountUpdateEvent:
    """Test AccountUpdateEvent model functionality."""

    def test_account_update_event_creation(self):
        """Test creating account update event."""
        event = AccountUpdateEventFactory()

        assert event.cash_balance is not None
        assert event.portfolio_value is not None
        assert event.buying_power is not None

    def test_account_update_event_initial_state(self):
        """Test account update event with initial state."""
        event = AccountUpdateEventFactory(
            cash_balance=Decimal("100000.00"),
            buying_power=Decimal("400000.00"),
            portfolio_value=Decimal("100000.00"),
            initial_margin=Decimal("0"),
            maintenance_margin=Decimal("0"),
        )

        assert_decimal_equal(event.cash_balance, Decimal("100000.00"))
        assert_decimal_equal(event.buying_power, Decimal("400000.00"))
        assert_decimal_equal(event.portfolio_value, Decimal("100000.00"))

    def test_account_update_event_with_positions(self):
        """Test account update event with open positions."""
        event = AccountUpdateEventFactory(
            cash_balance=Decimal("50000.00"), portfolio_value=Decimal("75000.00"), buying_power=Decimal("200000.00")  # Including position values
        )

        assert_decimal_equal(event.cash_balance, Decimal("50000.00"))
        assert_decimal_equal(event.portfolio_value, Decimal("75000.00"))

    def test_account_update_event_margin_usage(self):
        """Test account update event with margin usage."""
        # Account using margin (buying power < 4x cash)
        event = AccountUpdateEventFactory(
            cash_balance=Decimal("100000.00"),
            buying_power=Decimal("250000.00"),  # Less than 4x due to positions
            portfolio_value=Decimal("150000.00"),
            initial_margin=Decimal("100000.00"),
            margin_used=Decimal("50000.00"),
        )

        margin_utilization = event.margin_utilization
        assert margin_utilization == Decimal("50.0")  # 50% utilization


class TestTradeEvent:
    """Test TradeEvent model functionality."""

    def test_trade_event_creation(self):
        """Test creating trade event."""
        from tests.factories.events import TradeEventFactory

        event = TradeEventFactory()

        assert event.trade_id is not None
        assert event.order_id is not None
        assert event.symbol is not None
        assert event.quantity > 0
        assert event.price > 0

    def test_trade_event_buy_calculation(self):
        """Test trade event calculations for buy orders."""
        from tests.factories.events import TradeEventFactory

        event = TradeEventFactory(
            side=OrderSide.BUY, quantity=Decimal("100"), price=Decimal("150.00"), commission=Decimal("1.50"), fees=Decimal("0.50")
        )

        assert_decimal_equal(event.gross_value, Decimal("15000.00"))
        assert_decimal_equal(event.total_cost, Decimal("15002.00"))  # Including fees
        assert event.net_proceeds == Decimal("0")  # Only for sells

    def test_trade_event_sell_calculation(self):
        """Test trade event calculations for sell orders."""
        from tests.factories.events import TradeEventFactory

        event = TradeEventFactory(
            side=OrderSide.SELL, quantity=Decimal("100"), price=Decimal("150.00"), commission=Decimal("1.50"), fees=Decimal("0.50")
        )

        assert_decimal_equal(event.gross_value, Decimal("15000.00"))
        assert_decimal_equal(event.total_cost, Decimal("14998.00"))  # Subtracting fees
        assert_decimal_equal(event.net_proceeds, Decimal("14998.00"))


class TestSystemEvent:
    """Test SystemEvent model functionality."""

    def test_system_event_creation(self):
        """Test creating system event."""
        from tests.factories.events import SystemEventFactory

        event = SystemEventFactory()

        assert event.type is not None
        assert event.message is not None

    def test_system_event_connection_status(self):
        """Test system event for connection status."""
        from tektii.strategy.models.errors import SystemEventType
        from tests.factories.events import SystemEventFactory

        # Connected event
        connected_event = SystemEventFactory(type=SystemEventType.CONNECTED, message="Connected to market data feed")

        assert connected_event.type == SystemEventType.CONNECTED
        assert connected_event.is_connection_event
        assert not connected_event.is_error

        # Disconnected event
        disconnected_event = SystemEventFactory(type=SystemEventType.DISCONNECTED, message="Connection lost")

        assert disconnected_event.type == SystemEventType.DISCONNECTED
        assert disconnected_event.is_connection_event

    def test_system_event_error_types(self):
        """Test various system event error types."""
        from tektii.strategy.models.errors import SystemEventType
        from tests.factories.events import SystemEventFactory

        error_scenarios = [
            (SystemEventType.ERROR, "API error occurred"),
            (SystemEventType.WARNING, "High latency detected"),
            (SystemEventType.INFO, "System maintenance scheduled"),
        ]

        for event_type, message in error_scenarios:
            event = SystemEventFactory(type=event_type, message=message)

            assert event.type == event_type
            assert event.message == message

    def test_system_event_string_representation(self):
        """Test system event string representation."""
        from tektii.strategy.models.errors import SystemEventType
        from tests.factories.events import SystemEventFactory

        event = SystemEventFactory(type=SystemEventType.ERROR, message="Connection timeout")

        str_repr = str(event)
        assert "[3]" in str_repr  # SystemEventType.ERROR has value 3
        assert "Connection timeout" in str_repr
        assert "❌" in str_repr  # Error icon

    def test_system_event_with_details(self):
        """Test system event with additional details."""
        from tektii.strategy.models.errors import SystemEventType
        from tests.factories.events import SystemEventFactory

        event = SystemEventFactory(
            type=SystemEventType.WARNING, message="High latency detected", details={"latency_ms": "500", "threshold_ms": "200"}
        )

        assert event.details["latency_ms"] == "500"
        assert event.details["threshold_ms"] == "200"
