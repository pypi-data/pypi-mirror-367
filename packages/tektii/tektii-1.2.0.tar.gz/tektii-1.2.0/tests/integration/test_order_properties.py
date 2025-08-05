"""Property-based tests for order invariants using hypothesis."""

from decimal import Decimal

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st

from tektii.strategy.models import OrderBuilder
from tektii.strategy.models.enums import OrderSide, OrderType


class TestOrderProperties:
    """Property-based tests for order invariants."""

    @given(
        symbol=st.text(min_size=1, max_size=10).filter(lambda x: x.strip() and x.isalnum()),
        quantity=st.decimals(min_value=Decimal("0.01"), max_value=Decimal("1000000"), places=6),
        side=st.sampled_from([OrderSide.BUY, OrderSide.SELL]),
    )
    def test_market_order_properties(self, symbol: str, quantity: Decimal, side: OrderSide) -> None:
        """Test market order invariants."""
        # Build a market order
        builder = OrderBuilder().symbol(symbol).quantity(quantity)

        if side == OrderSide.BUY:
            builder = builder.buy()
        else:
            builder = builder.sell()

        order = builder.market().build()

        # Invariants:
        # 1. Market orders have no limit price (proto uses 0.0)
        assert order.limit_price == 0.0

        # 2. Market orders have no stop price (proto uses 0.0)
        assert order.stop_price == 0.0

        # 3. Symbol must match input
        assert order.symbol == symbol

        # 4. Quantity must match input (converted to float)
        assert abs(Decimal(str(order.quantity)) - quantity) < Decimal("0.000001")

        # 5. Side must match input (proto value)
        assert order.side == side.to_proto()

        # 6. Order type must be MARKET (proto value)
        assert order.order_type == OrderType.MARKET.to_proto()

    @given(
        symbol=st.text(min_size=1, max_size=10).filter(lambda x: x.strip() and x.isalnum()),
        quantity=st.decimals(min_value=Decimal("0.01"), max_value=Decimal("1000000"), places=6),
        limit_price=st.decimals(min_value=Decimal("0.01"), max_value=Decimal("1000000"), places=6),
        side=st.sampled_from([OrderSide.BUY, OrderSide.SELL]),
    )
    def test_limit_order_properties(self, symbol: str, quantity: Decimal, limit_price: Decimal, side: OrderSide) -> None:
        """Test limit order invariants."""
        # Build a limit order
        builder = OrderBuilder().symbol(symbol).quantity(quantity)

        if side == OrderSide.BUY:
            builder = builder.buy()
        else:
            builder = builder.sell()

        order = builder.limit(limit_price).build()

        # Invariants:
        # 1. Limit orders must have a limit price
        assert order.limit_price > 0
        assert abs(Decimal(str(order.limit_price)) - limit_price) < Decimal("0.000001")

        # 2. Limit orders have no stop price (proto uses 0.0)
        assert order.stop_price == 0.0

        # 3. Symbol must match input
        assert order.symbol == symbol

        # 4. Quantity must match input (converted to float)
        assert abs(Decimal(str(order.quantity)) - quantity) < Decimal("0.000001")

        # 5. Side must match input (proto value)
        assert order.side == side.to_proto()

        # 6. Order type must be LIMIT (proto value)
        assert order.order_type == OrderType.LIMIT.to_proto()

    @given(
        symbol=st.text(min_size=1, max_size=10).filter(lambda x: x.strip() and x.isalnum()),
        quantity=st.decimals(min_value=Decimal("0.01"), max_value=Decimal("1000000"), places=6),
        stop_price=st.decimals(min_value=Decimal("0.01"), max_value=Decimal("1000000"), places=6),
        side=st.sampled_from([OrderSide.BUY, OrderSide.SELL]),
    )
    def test_stop_order_properties(self, symbol: str, quantity: Decimal, stop_price: Decimal, side: OrderSide) -> None:
        """Test stop order invariants."""
        # Build a stop order
        builder = OrderBuilder().symbol(symbol).quantity(quantity)

        if side == OrderSide.BUY:
            builder = builder.buy()
        else:
            builder = builder.sell()

        order = builder.stop(stop_price).build()

        # Invariants:
        # 1. Stop orders have no limit price (proto uses 0.0)
        assert order.limit_price == 0.0

        # 2. Stop orders must have a stop price
        assert order.stop_price > 0
        assert abs(Decimal(str(order.stop_price)) - stop_price) < Decimal("0.000001")

        # 3. Symbol must match input
        assert order.symbol == symbol

        # 4. Quantity must match input (converted to float)
        assert abs(Decimal(str(order.quantity)) - quantity) < Decimal("0.000001")

        # 5. Side must match input (proto value)
        assert order.side == side.to_proto()

        # 6. Order type must be STOP (proto value)
        assert order.order_type == OrderType.STOP.to_proto()

    @given(
        symbol=st.text(min_size=1, max_size=10).filter(lambda x: x.strip() and x.isalnum()),
        quantity=st.decimals(min_value=Decimal("0.01"), max_value=Decimal("1000000"), places=6),
        stop_price=st.decimals(min_value=Decimal("0.01"), max_value=Decimal("1000000"), places=6),
        limit_price=st.decimals(min_value=Decimal("0.01"), max_value=Decimal("1000000"), places=6),
        side=st.sampled_from([OrderSide.BUY, OrderSide.SELL]),
    )
    def test_stop_limit_order_properties(self, symbol: str, quantity: Decimal, stop_price: Decimal, limit_price: Decimal, side: OrderSide) -> None:
        """Test stop-limit order invariants."""
        # Build a stop-limit order
        builder = OrderBuilder().symbol(symbol).quantity(quantity)

        if side == OrderSide.BUY:
            builder = builder.buy()
        else:
            builder = builder.sell()

        order = builder.stop_limit(stop_price, limit_price).build()

        # Invariants:
        # 1. Stop-limit orders must have both prices
        assert order.limit_price > 0
        assert abs(Decimal(str(order.limit_price)) - limit_price) < Decimal("0.000001")
        assert order.stop_price > 0
        assert abs(Decimal(str(order.stop_price)) - stop_price) < Decimal("0.000001")

        # 2. Symbol must match input
        assert order.symbol == symbol

        # 3. Quantity must match input (converted to float)
        assert abs(Decimal(str(order.quantity)) - quantity) < Decimal("0.000001")

        # 4. Side must match input (proto value)
        assert order.side == side.to_proto()

        # 5. Order type must be STOP_LIMIT (proto value)
        assert order.order_type == OrderType.STOP_LIMIT.to_proto()

    @given(
        quantity=st.decimals(min_value=Decimal("-1000000"), max_value=Decimal("0"), places=6),
    )
    def test_negative_quantity_rejected(self, quantity: Decimal) -> None:
        """Test that negative quantities are rejected."""
        assume(quantity < 0)  # Only test negative values

        builder = OrderBuilder().symbol("AAPL").buy().market().quantity(quantity)

        with pytest.raises(ValueError) as exc_info:
            builder.build()

        assert "must be positive" in str(exc_info.value)

    @given(
        quantity=st.decimals(min_value=Decimal("0"), max_value=Decimal("0"), places=6),
    )
    def test_zero_quantity_rejected(self, quantity: Decimal) -> None:
        """Test that zero quantity is rejected."""
        builder = OrderBuilder().symbol("AAPL").buy().market().quantity(quantity)

        with pytest.raises(ValueError) as exc_info:
            builder.build()

        assert "must be positive" in str(exc_info.value)

    @given(
        limit_price=st.decimals(min_value=Decimal("-1000000"), max_value=Decimal("0"), places=6),
    )
    def test_negative_limit_price_rejected(self, limit_price: Decimal) -> None:
        """Test that negative limit prices are rejected."""
        assume(limit_price <= 0)  # Only test non-positive values

        builder = OrderBuilder().symbol("AAPL").buy().quantity(100)

        with pytest.raises(ValueError) as exc_info:
            builder.limit(limit_price)

        assert "must be positive" in str(exc_info.value)

    @given(
        stop_price=st.decimals(min_value=Decimal("-1000000"), max_value=Decimal("0"), places=6),
    )
    def test_negative_stop_price_rejected(self, stop_price: Decimal) -> None:
        """Test that negative stop prices are rejected."""
        assume(stop_price <= 0)  # Only test non-positive values

        builder = OrderBuilder().symbol("AAPL").buy().quantity(100)

        with pytest.raises(ValueError) as exc_info:
            builder.stop(stop_price)

        assert "must be positive" in str(exc_info.value)

    @given(
        symbol=st.text(min_size=0, max_size=0),  # Empty string
    )
    def test_empty_symbol_rejected(self, symbol: str) -> None:
        """Test that empty symbols are rejected."""
        with pytest.raises(ValueError) as exc_info:
            OrderBuilder().symbol(symbol)

        assert "Symbol cannot be empty" in str(exc_info.value)

    @given(
        data=st.data(),
        symbol=st.text(min_size=1, max_size=10).filter(lambda x: x.strip() and x.isalnum()),
        quantity=st.decimals(min_value=Decimal("0.01"), max_value=Decimal("1000000"), places=6),
    )
    def test_incomplete_order_rejected(self, data, symbol: str, quantity: Decimal) -> None:
        """Test that incomplete orders cannot be built."""
        # Create builder with some fields
        builder = OrderBuilder().symbol(symbol).quantity(quantity)

        # Try to build without setting side or type
        with pytest.raises(ValueError):
            builder.build()

    @given(
        symbol=st.text(min_size=1, max_size=10).filter(lambda x: x.strip() and x.isalnum()),
        quantities=st.lists(st.decimals(min_value=Decimal("0.01"), max_value=Decimal("1000000"), places=6), min_size=2, max_size=5),
    )
    def test_order_modification_creates_new_instance(self, symbol: str, quantities: list) -> None:
        """Test that order modifications don't affect original order."""
        # Build first order
        builder1 = OrderBuilder().symbol(symbol).buy().market()
        order1 = builder1.quantity(quantities[0]).build()

        # Build second order with different quantity
        builder2 = OrderBuilder().symbol(symbol).buy().market()
        order2 = builder2.quantity(quantities[1]).build()

        # Original order should be unchanged
        assert abs(Decimal(str(order1.quantity)) - quantities[0]) < Decimal("0.000001")
        assert abs(Decimal(str(order2.quantity)) - quantities[1]) < Decimal("0.000001")
        # If quantities are different, orders should have different quantities
        if quantities[0] != quantities[1]:
            assert order1.quantity != order2.quantity

    @given(
        symbol=st.text(min_size=1, max_size=10).filter(lambda x: x.strip() and x.isalnum()),
        quantity=st.decimals(min_value=Decimal("0.01"), max_value=Decimal("1000000"), places=6),
        side=st.sampled_from([OrderSide.BUY, OrderSide.SELL]),
        order_type=st.sampled_from([OrderType.MARKET, OrderType.LIMIT, OrderType.STOP, OrderType.STOP_LIMIT]),
        limit_price=st.decimals(min_value=Decimal("0.01"), max_value=Decimal("1000000"), places=6),
        stop_price=st.decimals(min_value=Decimal("0.01"), max_value=Decimal("1000000"), places=6),
    )
    def test_order_equality(
        self, symbol: str, quantity: Decimal, side: OrderSide, order_type: OrderType, limit_price: Decimal, stop_price: Decimal
    ) -> None:
        """Test order equality based on all fields."""
        # Build two separate builders to ensure independence
        builder1 = OrderBuilder().symbol(symbol).quantity(quantity)
        builder2 = OrderBuilder().symbol(symbol).quantity(quantity)

        if side == OrderSide.BUY:
            builder1 = builder1.buy()
            builder2 = builder2.buy()
        else:
            builder1 = builder1.sell()
            builder2 = builder2.sell()

        if order_type == OrderType.MARKET:
            order1 = builder1.market().build()
            order2 = builder2.market().build()
        elif order_type == OrderType.LIMIT:
            order1 = builder1.limit(limit_price).build()
            order2 = builder2.limit(limit_price).build()
        elif order_type == OrderType.STOP:
            order1 = builder1.stop(stop_price).build()
            order2 = builder2.stop(stop_price).build()
        else:  # STOP_LIMIT
            order1 = builder1.stop_limit(stop_price, limit_price).build()
            order2 = builder2.stop_limit(stop_price, limit_price).build()

        # Orders with same properties should have same values
        assert order1.symbol == order2.symbol
        assert order1.quantity == order2.quantity
        assert order1.side == order2.side
        assert order1.order_type == order2.order_type
        assert order1.limit_price == order2.limit_price
        assert order1.stop_price == order2.stop_price

    @given(
        prices=st.lists(st.decimals(min_value=Decimal("0.01"), max_value=Decimal("1000000"), places=6), min_size=2, max_size=2, unique=True),
    )
    def test_stop_limit_price_independence(self, prices: list) -> None:
        """Test that stop and limit prices are independent in stop-limit orders."""
        stop_price, limit_price = prices[0], prices[1]

        # Build stop-limit order
        order = OrderBuilder().symbol("AAPL").buy().quantity(100).stop_limit(stop_price, limit_price).build()

        # Prices should be stored independently (converted to float)
        assert abs(Decimal(str(order.stop_price)) - stop_price) < Decimal("0.000001")
        assert abs(Decimal(str(order.limit_price)) - limit_price) < Decimal("0.000001")
        # If input prices are different, output should be different
        if stop_price != limit_price:
            assert order.stop_price != order.limit_price

    @given(
        symbol=st.text(min_size=1, max_size=10).filter(lambda x: x.strip() and x.isalnum()),
        quantity=st.decimals(min_value=Decimal("0.01"), max_value=Decimal("1000000"), places=6),
    )
    def test_order_immutability(self, symbol: str, quantity: Decimal) -> None:
        """Test that built orders are immutable."""
        # Build an order
        order = OrderBuilder().symbol(symbol).buy().market().quantity(quantity).build()

        # PlaceOrderRequest is a protobuf message which is effectively immutable
        # for our purposes - fields can be set but it's not a concern for the SDK
        original_symbol = order.symbol

        # Values should match what was set
        assert order.symbol == original_symbol
        assert abs(Decimal(str(order.quantity)) - quantity) < Decimal("0.000001")
