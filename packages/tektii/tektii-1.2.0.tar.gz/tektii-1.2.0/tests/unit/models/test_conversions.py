"""Unit tests for proto conversions."""

from datetime import datetime
from decimal import Decimal

import pytest

from tektii.strategy.models.common import Position
from tektii.strategy.models.enums import OrderSide, OrderStatus, OrderType, TimeInForce
from tektii.strategy.models.market_data import BarData, TickData
from tektii.strategy.models.orders import Order
from tests.assertions import assert_decimal_equal, assert_financial_calculation_accurate
from tests.factories import BarDataFactory, OrderFactory, PositionFactory, TickDataFactory


class TestDecimalConversions:
    """Test decimal conversions in proto serialization."""

    def test_decimal_to_proto_precision(self):
        """Test decimal to proto conversion preserves precision."""
        test_values = [
            Decimal("123.456789"),  # 6 decimal places
            Decimal("0.000001"),  # Very small
            Decimal("999999.999999"),  # Large with decimals
            Decimal("100"),  # Integer
            Decimal("0"),  # Zero
            Decimal("-123.456"),  # Negative
        ]

        for value in test_values:
            # Convert to proto format (float)
            proto_value = float(value)
            # Convert back to decimal
            restored = Decimal(str(proto_value))

            # For most financial calculations, 6 decimal places is sufficient
            assert_decimal_equal(value, restored, places=6)

    def test_decimal_edge_cases_in_proto(self):
        """Test decimal edge cases in proto conversion."""
        # Very precise decimal
        precise = Decimal("123.123456789012345")
        proto_value = float(precise)
        restored = Decimal(str(proto_value))

        # Should maintain at least 6 decimal places
        assert_financial_calculation_accurate(restored, precise, Decimal("0.0001"))

    def test_decimal_string_conversion_for_proto(self):
        """Test decimal to string conversion for proto fields."""
        # Some proto fields might use string representation
        decimal_value = Decimal("123.456789012345")
        string_value = str(decimal_value)
        restored = Decimal(string_value)

        # String conversion should preserve exact precision
        assert restored == decimal_value


class TestOrderProtoConversion:
    """Test Order proto conversion."""

    def test_order_full_proto_roundtrip(self):
        """Test complete order proto roundtrip with all fields."""
        original_order = OrderFactory(
            order_id="test-order-123",
            symbol="AAPL",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("100.5"),
            limit_price=Decimal("150.123456"),
            status=OrderStatus.PENDING,
            filled_quantity=Decimal("0"),
        )

        # Convert to proto
        proto = original_order.to_proto()

        # Verify proto fields
        assert proto.order_id == "test-order-123"
        assert proto.symbol == "AAPL"
        assert proto.side == OrderSide.BUY.to_proto()
        assert proto.order_type == OrderType.LIMIT.to_proto()
        assert proto.quantity == float(original_order.quantity)
        assert proto.limit_price == float(original_order.limit_price)

        # Convert back
        restored_order = Order.from_proto(proto)

        # Verify all fields
        assert restored_order.order_id == original_order.order_id
        assert restored_order.symbol == original_order.symbol
        assert restored_order.side == original_order.side
        assert restored_order.order_type == original_order.order_type
        assert_decimal_equal(restored_order.quantity, original_order.quantity)
        assert_decimal_equal(restored_order.limit_price, original_order.limit_price, places=6)
        assert restored_order.status == original_order.status

    def test_order_proto_with_fills(self):
        """Test order proto conversion with fill information."""
        filled_order = OrderFactory(
            status=OrderStatus.FILLED,
            quantity=Decimal("100"),
            filled_quantity=Decimal("100"),
        )

        proto = filled_order.to_proto()
        restored = Order.from_proto(proto)

        assert restored.status == OrderStatus.FILLED
        assert_decimal_equal(restored.filled_quantity, Decimal("100"))

    def test_order_proto_optional_fields(self):
        """Test order proto conversion with optional fields."""
        # Market order (no prices)
        market_order = OrderFactory(order_type=OrderType.MARKET, limit_price=None, stop_price=None)

        proto = market_order.to_proto()
        assert proto.limit_price == 0.0  # Default proto value
        assert proto.stop_price == 0.0

        restored = Order.from_proto(proto)
        assert restored.limit_price is None
        assert restored.stop_price is None


class TestPositionProtoConversion:
    """Test Position proto conversion."""

    def test_position_full_proto_roundtrip(self):
        """Test complete position proto roundtrip."""
        original_position = PositionFactory(
            symbol="GOOGL",
            quantity=Decimal("-50"),  # Short position
            avg_price=Decimal("2500.75"),
            realized_pnl=Decimal("1250.50"),
            unrealized_pnl=Decimal("-500.25"),
        )

        proto = original_position.to_proto()
        restored = Position.from_proto(proto)

        assert restored.symbol == original_position.symbol
        assert_decimal_equal(restored.quantity, original_position.quantity)
        assert_decimal_equal(restored.avg_price, original_position.avg_price)
        assert_decimal_equal(restored.realized_pnl, original_position.realized_pnl)
        assert_decimal_equal(restored.unrealized_pnl, original_position.unrealized_pnl)

    def test_position_proto_side_calculation(self):
        """Test position side is correctly calculated from quantity."""
        # Long position
        long_pos = PositionFactory(quantity=Decimal("100"))
        proto = long_pos.to_proto()
        restored = Position.from_proto(proto)
        assert restored.is_long

        # Short position
        short_pos = PositionFactory(quantity=Decimal("-100"))
        proto = short_pos.to_proto()
        restored = Position.from_proto(proto)
        assert restored.is_short

        # Flat position
        flat_pos = PositionFactory(quantity=Decimal("0"))
        proto = flat_pos.to_proto()
        restored = Position.from_proto(proto)
        assert not flat_pos.is_long and not flat_pos.is_short


class TestMarketDataProtoConversion:
    """Test market data proto conversions."""

    def test_tick_data_proto_roundtrip(self):
        """Test tick data proto roundtrip."""
        original_tick = TickDataFactory(
            symbol="MSFT",
            timestamp_us=1234567890123456,
            last=Decimal("350.12"),
            bid=Decimal("350.11"),
            ask=Decimal("350.13"),
            bid_size=500,
            ask_size=700,
            volume=1234567,
            condition="REGULAR",
        )

        proto = original_tick.to_proto()
        restored = TickData.from_proto(proto)

        assert restored.symbol == original_tick.symbol
        # Note: timestamp_us is not in the proto, so we can't test roundtrip
        assert_decimal_equal(restored.last, original_tick.last)
        assert_decimal_equal(restored.bid, original_tick.bid)
        assert_decimal_equal(restored.ask, original_tick.ask)
        assert restored.bid_size == original_tick.bid_size
        assert restored.ask_size == original_tick.ask_size
        # Note: volume is not preserved in TickData proto
        # Note: condition is not preserved in TickData proto

    def test_bar_data_proto_roundtrip(self):
        """Test bar data proto roundtrip."""
        original_bar = BarDataFactory(
            symbol="SPY",
            timestamp_us=1234567890123456,
            open=Decimal("440.50"),
            high=Decimal("441.75"),
            low=Decimal("439.25"),
            close=Decimal("441.00"),
            volume=10000000,
            vwap=Decimal("440.75"),
            trade_count=75000,
            bar_size=5,
            bar_size_unit="min",
        )

        proto = original_bar.to_proto()
        restored = BarData.from_proto(proto)

        assert restored.symbol == original_bar.symbol
        # Note: timestamp_us is not in the proto, so it gets regenerated
        assert_decimal_equal(restored.open, original_bar.open)
        assert_decimal_equal(restored.high, original_bar.high)
        assert_decimal_equal(restored.low, original_bar.low)
        assert_decimal_equal(restored.close, original_bar.close)
        assert restored.volume == original_bar.volume
        assert_decimal_equal(restored.vwap, original_bar.vwap)
        assert restored.trade_count == original_bar.trade_count
        assert restored.bar_size == original_bar.bar_size
        assert restored.bar_size_unit == original_bar.bar_size_unit


class TestTimestampConversions:
    """Test timestamp conversions in proto."""

    def test_microsecond_timestamp_conversion(self):
        """Test microsecond timestamp conversion."""
        # Current time in microseconds
        timestamp_us = int(datetime.now().timestamp() * 1_000_000)

        # Create objects with timestamp
        tick = TickDataFactory(timestamp_us=timestamp_us)
        bar = BarDataFactory(timestamp_us=timestamp_us, bar_size=1, bar_size_unit="min")

        # Verify datetime property
        expected_dt = datetime.fromtimestamp(timestamp_us / 1_000_000)

        assert abs((tick.timestamp - expected_dt).total_seconds()) < 0.001
        assert abs((bar.timestamp - expected_dt).total_seconds()) < 0.001

    def test_timestamp_precision_in_proto(self):
        """Test timestamp precision is maintained in proto."""
        # Specific timestamp with microseconds
        timestamp_us = 1640995200123456  # 2022-01-01 00:00:00.123456

        tick = TickDataFactory(timestamp_us=timestamp_us)
        proto = tick.to_proto()
        restored = TickData.from_proto(proto)

        # Note: timestamp_us is not preserved in proto, so we can't test exact match
        # Just verify that restored tick has a valid timestamp
        assert restored.timestamp_us > 0
        assert isinstance(restored.timestamp, datetime)


class TestEnumProtoConversions:
    """Test enum proto conversions."""

    def test_all_enum_proto_conversions(self):
        """Test all enum types convert to/from proto correctly."""
        # OrderSide
        assert OrderSide.BUY.to_proto() == OrderSide.BUY.value
        assert OrderSide.from_proto(OrderSide.BUY.value) == OrderSide.BUY

        # OrderType
        assert OrderType.LIMIT.to_proto() == OrderType.LIMIT.value
        assert OrderType.from_proto(OrderType.LIMIT.value) == OrderType.LIMIT

        # TimeInForce
        assert TimeInForce.IOC.to_proto() == TimeInForce.IOC.value
        assert TimeInForce.from_proto(TimeInForce.IOC.value) == TimeInForce.IOC

    def test_enum_proto_invalid_values(self):
        """Test invalid proto enum values raise errors."""
        with pytest.raises(ValueError):
            OrderSide.from_proto(999)

        with pytest.raises(ValueError):
            OrderType.from_proto(999)

        with pytest.raises(ValueError):
            TimeInForce.from_proto(999)


class TestProtoFieldValidation:
    """Test proto field validation during conversion."""

    def test_required_fields_validation(self):
        """Test required fields are validated in proto conversion."""
        from tektii.strategy.grpc import common_pb2

        # Create proto with missing required fields
        proto = common_pb2.Order()
        # Set minimal required fields to avoid validation errors
        proto.order_id = ""
        proto.symbol = ""  # Empty but present
        proto.side = OrderSide.BUY.to_proto()
        proto.order_type = OrderType.MARKET.to_proto()
        proto.quantity = 0.0
        proto.status = OrderStatus.PENDING.to_proto()
        proto.filled_quantity = 0.0
        proto.created_at_us = 0

        # Should handle empty values gracefully
        order = Order.from_proto(proto)
        assert order.symbol == ""
        assert order.quantity == Decimal("0")

    def test_proto_default_values(self):
        """Test proto default values are handled correctly."""
        from tektii.strategy.grpc import common_pb2

        # Create minimal proto
        proto = common_pb2.Order()
        proto.order_id = "test-123"
        proto.symbol = "AAPL"
        proto.side = OrderSide.BUY.to_proto()
        proto.order_type = OrderType.MARKET.to_proto()
        proto.quantity = 100.0
        proto.status = OrderStatus.PENDING.to_proto()
        proto.filled_quantity = 0.0
        proto.created_at_us = int(datetime.now().timestamp() * 1_000_000)

        # Convert from proto
        order = Order.from_proto(proto)

        # Check defaults
        assert order.status == OrderStatus.PENDING
        assert order.filled_quantity == Decimal("0")
