"""Unit tests for Order and OrderBuilder models."""

from decimal import Decimal

import pytest

from tektii.strategy.models.enums import OrderIntent, OrderSide, OrderStatus, OrderType, TimeInForce
from tektii.strategy.models.orders import Order, OrderBuilder
from tests.assertions import assert_decimal_equal, assert_order_valid, assert_proto_conversion_preserves_data
from tests.factories import OrderFactory


class TestOrderBuilder:
    """Test OrderBuilder fluent API."""

    def test_fluent_api_creates_valid_market_order(self):
        """Test fluent API creates valid market orders."""
        order = OrderBuilder().symbol("AAPL").buy().market().quantity(100).build()

        assert order.symbol == "AAPL"
        assert order.side == OrderSide.BUY.to_proto()
        assert order.order_type == OrderType.MARKET.to_proto()
        assert order.quantity == float(Decimal("100"))
        assert order.limit_price == 0.0
        assert order.stop_price == 0.0

    def test_fluent_api_creates_valid_limit_order(self):
        """Test fluent API creates valid limit orders."""
        order = OrderBuilder().symbol("GOOGL").sell().limit(2500.50).quantity(50).time_in_force(TimeInForce.GTC).build()

        assert order.symbol == "GOOGL"
        assert order.side == OrderSide.SELL.to_proto()
        assert order.order_type == OrderType.LIMIT.to_proto()
        assert order.quantity == float(Decimal("50"))
        assert_decimal_equal(Decimal(str(order.limit_price)), Decimal("2500.50"))
        assert order.time_in_force == TimeInForce.GTC.to_proto()

    def test_fluent_api_creates_valid_stop_order(self):
        """Test fluent API creates valid stop orders."""
        order = OrderBuilder().symbol("SPY").sell().stop(400.00).quantity(200).build()

        assert order.symbol == "SPY"
        assert order.side == OrderSide.SELL.to_proto()
        assert order.order_type == OrderType.STOP.to_proto()
        assert order.quantity == float(Decimal("200"))
        assert_decimal_equal(Decimal(str(order.stop_price)), Decimal("400.00"))

    def test_fluent_api_creates_valid_stop_limit_order(self):
        """Test fluent API creates valid stop-limit orders."""
        order = (
            OrderBuilder()
            .symbol("MSFT")
            .buy()
            .stop_limit(350.00, 351.00)
            .quantity(75)
            .metadata("strategy", "breakout")
            .metadata("signal", "bullish")
            .build()
        )

        assert order.symbol == "MSFT"
        assert order.side == OrderSide.BUY.to_proto()
        assert order.order_type == OrderType.STOP_LIMIT.to_proto()
        assert order.quantity == float(Decimal("75"))
        assert_decimal_equal(Decimal(str(order.stop_price)), Decimal("350.00"))
        assert_decimal_equal(Decimal(str(order.limit_price)), Decimal("351.00"))
        assert order.metadata["strategy"] == "breakout"
        assert order.metadata["signal"] == "bullish"

    def test_validation_prevents_invalid_orders(self):
        """Test validation catches invalid orders."""
        # Missing symbol
        with pytest.raises(ValueError, match="Symbol is required"):
            OrderBuilder().buy().market().quantity(100).build()

        # Missing side
        with pytest.raises(ValueError, match="Side is required"):
            OrderBuilder().symbol("AAPL").market().quantity(100).build()

        # Missing quantity
        with pytest.raises(ValueError, match="Quantity must be positive"):
            OrderBuilder().symbol("AAPL").buy().market().build()

        # Negative quantity
        with pytest.raises(ValueError, match="Quantity must be positive"):
            OrderBuilder().symbol("AAPL").buy().market().quantity(-100).build()

        # Zero quantity
        with pytest.raises(ValueError, match="Quantity must be positive"):
            OrderBuilder().symbol("AAPL").buy().market().quantity(0).build()

        # Limit order without price
        with pytest.raises(ValueError, match="requires limit price"):
            OrderBuilder().symbol("AAPL").buy().limit(0).quantity(100).build()

        # Stop order without price
        with pytest.raises(ValueError, match="requires stop price"):
            OrderBuilder().symbol("AAPL").sell().stop(0).quantity(100).build()

    def test_builder_accepts_decimal_inputs(self):
        """Test builder properly handles Decimal inputs."""
        order = OrderBuilder().symbol("AAPL").buy().limit(Decimal("150.25")).quantity(Decimal("100.5")).build()

        assert order.limit_price == float(Decimal("150.25"))
        assert order.quantity == float(Decimal("100.5"))

    def test_builder_chain_methods_return_self(self):
        """Test all builder methods return self for chaining."""
        builder = OrderBuilder()

        assert builder.symbol("AAPL") is builder
        assert builder.buy() is builder
        assert builder.sell() is builder
        assert builder.market() is builder
        assert builder.limit(100) is builder
        assert builder.stop(100) is builder
        assert builder.stop_limit(100, 101) is builder
        assert builder.quantity(100) is builder
        assert builder.time_in_force(TimeInForce.DAY) is builder


class TestOrder:
    """Test Order model functionality."""

    def test_order_creation_with_factory(self):
        """Test creating orders with factory."""
        order = OrderFactory()
        assert_order_valid(order)

    def test_order_string_representation(self):
        """Test order string representation."""
        order = OrderFactory(
            symbol="AAPL",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("100"),
            limit_price=Decimal("150.00"),
        )

        str_repr = str(order)
        assert "AAPL" in str_repr
        assert "BUY" in str_repr
        assert "LIMIT" in str_repr
        assert "100" in str_repr
        assert "150.00" in str_repr

    def test_order_calculate_value(self):
        """Test order value calculation."""
        # Market order - no value
        market_order = OrderFactory(order_type=OrderType.MARKET, quantity=Decimal("100"))
        assert market_order.calculate_value() is None

        # Limit order
        limit_order = OrderFactory(
            order_type=OrderType.LIMIT,
            quantity=Decimal("100"),
            limit_price=Decimal("150.50"),
        )
        assert_decimal_equal(limit_order.calculate_value(), Decimal("15050.00"))

        # Stop order
        stop_order = OrderFactory(
            order_type=OrderType.STOP,
            quantity=Decimal("50"),
            stop_price=Decimal("145.00"),
        )
        assert_decimal_equal(stop_order.calculate_value(), Decimal("7250.00"))

    def test_order_is_filled_property(self):
        """Test is_filled property."""
        # Test with different filled states by creating new orders
        # Not filled
        unfilled_order = OrderFactory(quantity=Decimal("100"), filled_quantity=Decimal("0"), status=OrderStatus.PENDING)
        assert not unfilled_order.is_filled

        # Partially filled
        partial_order = OrderFactory(quantity=Decimal("100"), filled_quantity=Decimal("50"), status=OrderStatus.PARTIAL)
        assert not partial_order.is_filled

        # Fully filled
        filled_order = OrderFactory(quantity=Decimal("100"), filled_quantity=Decimal("100"), status=OrderStatus.FILLED)
        assert filled_order.is_filled

    def test_order_is_active_property(self):
        """Test is_active property."""
        # Test with different statuses by creating new orders
        # Active statuses
        for status in [OrderStatus.PENDING, OrderStatus.ACCEPTED, OrderStatus.PARTIAL]:
            order = OrderFactory(status=status)
            assert order.is_active

        # Inactive statuses
        for status in [OrderStatus.FILLED, OrderStatus.CANCELED, OrderStatus.REJECTED]:
            order = OrderFactory(status=status)
            assert not order.is_active

    def test_order_proto_conversion(self):
        """Test order proto conversion preserves all data."""
        from tektii.strategy.grpc import common_pb2

        # Test various order types
        for order_type in [OrderType.MARKET, OrderType.LIMIT, OrderType.STOP, OrderType.STOP_LIMIT]:
            order = OrderFactory(order_type=order_type)
            assert_proto_conversion_preserves_data(order, common_pb2.Order, Order)

    def test_order_with_metadata(self):
        """Test order intent and parent trade ID for tracking metadata."""
        # Note: Order model doesn't have a metadata field
        # We can use order_intent and parent_trade_id for tracking purposes

        order = OrderFactory(order_intent=OrderIntent.OPEN, parent_trade_id="momentum_strategy_001")

        assert order.order_intent == OrderIntent.OPEN
        assert order.parent_trade_id == "momentum_strategy_001"

        # Test proto conversion preserves these fields
        proto = order.to_proto()
        restored = Order.from_proto(proto)
        assert restored.order_intent == order.order_intent
        assert restored.parent_trade_id == order.parent_trade_id

    def test_decimal_precision_preservation(self):
        """Test decimal precision is preserved throughout order lifecycle."""
        # Create order with precise decimal values
        price = Decimal("123.456789")
        quantity = Decimal("100.123456")

        order = OrderFactory(
            limit_price=price,
            quantity=quantity,
        )

        # Verify exact precision preservation
        assert_decimal_equal(order.limit_price, price)
        assert_decimal_equal(order.quantity, quantity)

        # Test proto round-trip
        proto_order = order.to_proto()
        restored_order = Order.from_proto(proto_order)

        # Proto conversion loses some precision for floats
        assert_decimal_equal(restored_order.limit_price, price, places=6)
        assert_decimal_equal(restored_order.quantity, quantity, places=6)

    def test_order_validation_edge_cases(self):
        """Test order validation edge cases."""
        # Very small quantity
        small_qty_order = OrderFactory(quantity=Decimal("0.000001"))
        assert_order_valid(small_qty_order)

        # Very large quantity
        large_qty_order = OrderFactory(quantity=Decimal("1000000000"))
        assert_order_valid(large_qty_order)

        # High precision price
        precise_price_order = OrderFactory(order_type=OrderType.LIMIT, limit_price=Decimal("150.123456"), quantity=100)
        assert_order_valid(precise_price_order)
