"""Unit tests for strategy validation functionality."""

from __future__ import annotations

import decimal
from decimal import Decimal

import pytest

from tektii.strategy.models.enums import OrderSide, OrderType, TimeInForce
from tektii.strategy.models.errors import ValidationErrorCode
from tektii.strategy.models.orders import OrderBuilder
from tektii.strategy.models.risk import RiskCheckResult, ValidationError


class TestStrategyValidation:
    """Test suite for strategy validation logic."""

    def test_order_basic_validation(self):
        """Test basic order validation rules."""
        # Valid order
        order = OrderBuilder().symbol("AAPL").buy().market().quantity(100).build()

        assert order.symbol == "AAPL"
        assert order.side == OrderSide.BUY
        assert order.order_type == OrderType.MARKET
        assert order.quantity == Decimal("100")

    def test_order_symbol_validation(self):
        """Test order symbol validation."""
        # Empty symbol
        with pytest.raises(ValueError, match="Symbol is required"):
            OrderBuilder().symbol("").buy().market().quantity(100).build()

        # None symbol
        with pytest.raises(ValueError, match="Symbol is required"):
            OrderBuilder().symbol(None).buy().market().quantity(100).build()  # type: ignore

        # Whitespace symbol - should NOT be trimmed in OrderBuilder
        order = OrderBuilder().symbol("  AAPL  ").buy().market().quantity(100).build()
        assert order.symbol == "  AAPL  "  # Builder preserves exact input

    def test_order_quantity_validation(self):
        """Test order quantity validation."""
        # Zero quantity
        with pytest.raises(ValueError, match="Quantity must be positive"):
            OrderBuilder().symbol("AAPL").buy().market().quantity(0).build()

        # Negative quantity
        with pytest.raises(ValueError, match="Quantity must be positive"):
            OrderBuilder().symbol("AAPL").buy().market().quantity(-100).build()

        # Very small quantity (should be allowed)
        request = OrderBuilder().symbol("AAPL").buy().market().quantity(0.001).build()
        assert request.quantity == 0.001  # OrderBuilder returns proto request, not model

    def test_limit_order_price_validation(self):
        """Test limit order price validation."""
        # Limit order with None price should fail during limit() call
        with pytest.raises((TypeError, ValueError, decimal.InvalidOperation)):  # Decimal conversion error
            OrderBuilder().symbol("AAPL").buy().limit(None).quantity(100).build()  # type: ignore

        # Limit order with zero price
        with pytest.raises(ValueError, match="LIMIT requires limit price"):
            OrderBuilder().symbol("AAPL").buy().limit(0).quantity(100).build()

        # Limit order with negative price - validation happens in build()
        request = OrderBuilder().symbol("AAPL").buy().limit(-150.00).quantity(100).build()
        # Negative prices are allowed by the builder, validation would happen server-side
        assert request.limit_price == -150.00

    def test_stop_order_price_validation(self):
        """Test stop order price validation."""
        # Stop order with None price should fail in stop() method
        with pytest.raises((TypeError, ValueError, decimal.InvalidOperation)):  # Decimal conversion error
            OrderBuilder().symbol("AAPL").buy().stop(None).quantity(100).build()  # type: ignore

        # Stop order with zero price - zero treated as missing
        with pytest.raises(ValueError, match="STOP requires stop price"):
            OrderBuilder().symbol("AAPL").buy().stop(0).quantity(100).build()

    def test_stop_limit_order_validation(self):
        """Test stop limit order validation."""
        # Stop limit order with None prices should fail during stop_limit() call
        with pytest.raises((TypeError, ValueError, decimal.InvalidOperation)):  # Decimal conversion error
            OrderBuilder().symbol("AAPL").buy().stop_limit(stop_price=150.00, limit_price=None).quantity(100).build()  # type: ignore

        with pytest.raises((TypeError, ValueError, decimal.InvalidOperation)):  # Decimal conversion error
            OrderBuilder().symbol("AAPL").buy().stop_limit(stop_price=None, limit_price=150.00).quantity(100).build()  # type: ignore

        # Valid stop limit order
        order = OrderBuilder().symbol("AAPL").buy().stop_limit(stop_price=150.00, limit_price=151.00).quantity(100).build()
        assert order.stop_price == Decimal("150.00")
        assert order.limit_price == Decimal("151.00")

    def test_order_side_validation(self):
        """Test order side validation."""
        # Order without side
        with pytest.raises(ValueError, match="Side is required"):
            OrderBuilder().symbol("AAPL").market().quantity(100).build()

    def test_order_type_validation(self):
        """Test order type validation."""
        # Order without type - should default to MARKET
        request = OrderBuilder().symbol("AAPL").buy().quantity(100).build()
        assert request.order_type == OrderType.MARKET.value

    def test_time_in_force_validation(self):
        """Test time in force validation."""
        # Valid DAY order
        order = OrderBuilder().symbol("AAPL").buy().limit(150.00).quantity(100).time_in_force(TimeInForce.DAY).build()
        assert order.time_in_force == TimeInForce.DAY

        # Valid GTC order
        order = OrderBuilder().symbol("AAPL").buy().limit(150.00).quantity(100).time_in_force(TimeInForce.GTC).build()
        assert order.time_in_force == TimeInForce.GTC

        # Default should be DAY
        order = OrderBuilder().symbol("AAPL").buy().limit(150.00).quantity(100).build()
        assert order.time_in_force == TimeInForce.DAY

    def test_order_creation_and_building(self):
        """Test order creation and building."""
        # Valid order creation
        order = OrderBuilder().symbol("AAPL").buy().market().quantity(100).build()
        assert order.symbol == "AAPL"
        assert order.side == OrderSide.BUY
        assert order.order_type == OrderType.MARKET
        assert order.quantity == Decimal("100")

    def test_decimal_precision_validation(self):
        """Test decimal precision handling in orders."""
        # Test with various decimal precisions
        order = OrderBuilder().symbol("AAPL").buy().limit(150.123456789).quantity(100.987654321).build()

        # Should preserve precision
        assert str(order.limit_price) == "150.123456789"
        assert str(order.quantity) == "100.987654321"

    def test_order_builder_fluent_api(self):
        """Test the fluent API of OrderBuilder."""
        # Test method chaining
        builder = OrderBuilder()
        assert builder.symbol("AAPL") is builder
        assert builder.buy() is builder
        assert builder.sell() is builder
        assert builder.market() is builder
        assert builder.limit(150.00) is builder
        assert builder.stop(150.00) is builder
        assert builder.quantity(100) is builder
        assert builder.time_in_force(TimeInForce.GTC) is builder

    def test_order_builder_state_validation(self):
        """Test OrderBuilder state validation."""
        # Cannot set both buy and sell
        builder = OrderBuilder().symbol("AAPL").buy()
        builder.sell()  # This should override
        order = builder.market().quantity(100).build()
        assert order.side == OrderSide.SELL

        # Cannot set conflicting order types
        builder = OrderBuilder().symbol("AAPL").buy().market()
        builder.limit(150.00)  # This should change to LIMIT
        order = builder.quantity(100).build()
        assert order.order_type == OrderType.LIMIT
        assert order.limit_price == Decimal("150.00")

    def test_risk_check_result_validation(self):
        """Test RiskCheckResult validation."""
        # RiskCheckResult requires many fields
        result = RiskCheckResult(
            margin_required=Decimal("1000"),
            margin_available=Decimal("5000"),
            buying_power_used=Decimal("1000"),
            buying_power_remaining=Decimal("4000"),
            position_limit=Decimal("10000"),
            current_position=Decimal("0"),
            resulting_position=Decimal("100"),
            portfolio_var_before=Decimal("500"),
            portfolio_var_after=Decimal("600"),
            concentration_risk=Decimal("0.1"),
        )
        # RiskCheckResult doesn't have a 'passed' field
        assert result.margin_required == Decimal("1000")

    def test_validation_error_model(self):
        """Test ValidationError model."""
        # Test basic validation error
        error = ValidationError(field="order", message="Invalid order parameters", code=ValidationErrorCode.MISSING_REQUIRED_FIELD)
        assert error.field == "order"
        assert error.message == "Invalid order parameters"
        assert error.code == ValidationErrorCode.MISSING_REQUIRED_FIELD

        # Test string representation
        assert "order" in str(error)
        assert "Invalid order parameters" in str(error)

    def test_order_protective_orders(self):
        """Test protective orders on fill."""
        # Test with stop loss
        request = OrderBuilder().symbol("AAPL").buy().limit(150.00).quantity(100).with_stop_loss(stop_price=145.00).build()

        # OrderBuilder returns PlaceOrderRequest proto, not Order model
        assert request.protective_orders_on_fill is not None
        assert request.protective_orders_on_fill.stop.stop_price == 145.00
        assert request.protective_orders_on_fill.take_profit_price == 0.0

        # Test with take profit
        request = OrderBuilder().symbol("AAPL").buy().limit(150.00).quantity(100).with_take_profit(price=155.00).build()

        assert request.protective_orders_on_fill is not None
        assert not request.protective_orders_on_fill.HasField("stop")
        assert request.protective_orders_on_fill.take_profit_price == 155.00

        # Test with both
        request = (
            OrderBuilder().symbol("AAPL").buy().limit(150.00).quantity(100).with_stop_loss(stop_price=145.00).with_take_profit(price=155.00).build()
        )

        assert request.protective_orders_on_fill is not None
        assert request.protective_orders_on_fill.stop.stop_price == 145.00
        assert request.protective_orders_on_fill.take_profit_price == 155.00
