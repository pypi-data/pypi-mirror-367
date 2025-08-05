"""Order test factories."""

import time
import uuid
from decimal import Decimal

import factory

from tektii.strategy.models.enums import OrderIntent, OrderSide, OrderStatus, OrderType
from tektii.strategy.models.orders import Order, OrderBuilder


class OrderFactory(factory.Factory):
    """Factory for creating test orders."""

    class Meta:
        model = Order

    order_id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    symbol = factory.Faker("random_element", elements=["AAPL", "GOOGL", "MSFT", "SPY", "QQQ"])
    side = factory.Faker("random_element", elements=[OrderSide.BUY, OrderSide.SELL])
    order_type = factory.Faker("random_element", elements=[OrderType.MARKET, OrderType.LIMIT, OrderType.STOP, OrderType.STOP_LIMIT])
    quantity = factory.LazyFunction(lambda: Decimal(factory.Faker._get_faker().pyint(min_value=1, max_value=1000)))
    filled_quantity = factory.LazyFunction(lambda: Decimal("0"))
    limit_price = factory.Maybe(
        factory.LazyAttribute(lambda obj: obj.order_type in [OrderType.LIMIT, OrderType.STOP_LIMIT]),
        yes_declaration=factory.LazyFunction(lambda: Decimal(factory.Faker._get_faker().pydecimal(left_digits=3, right_digits=2, positive=True))),
        no_declaration=None,
    )
    stop_price = factory.Maybe(
        factory.LazyAttribute(lambda obj: obj.order_type in [OrderType.STOP, OrderType.STOP_LIMIT]),
        yes_declaration=factory.LazyFunction(lambda: Decimal(factory.Faker._get_faker().pydecimal(left_digits=3, right_digits=2, positive=True))),
        no_declaration=None,
    )
    status = factory.Faker("random_element", elements=list(OrderStatus))
    created_at_us = factory.LazyFunction(lambda: int(time.time() * 1_000_000))
    order_intent = factory.Faker("random_element", elements=list(OrderIntent))
    parent_trade_id = None

    def calculate_value(self):
        """Calculate order value for testing."""
        if self.order_type == OrderType.MARKET:
            return None
        elif self.order_type in [OrderType.LIMIT, OrderType.STOP_LIMIT] and self.limit_price:
            return self.quantity * self.limit_price
        elif self.order_type == OrderType.STOP and self.stop_price:
            return self.quantity * self.stop_price
        return None

    @property
    def is_filled(self):
        """Check if order is filled."""
        return self.status == OrderStatus.FILLED

    @property
    def is_active(self):
        """Check if order is active."""
        return self.status.is_active()

    @property
    def remaining_quantity(self):
        """Calculate remaining quantity."""
        return self.quantity - self.filled_quantity


class OrderBuilderFactory(factory.Factory):
    """Factory for creating test order builders."""

    class Meta:
        model = OrderBuilder

    # OrderBuilder doesn't store state, it's a builder pattern
    # This factory is primarily for testing the builder itself
    @classmethod
    def create_simple_order(cls, **kwargs):
        """Create a simple order using the builder."""
        builder = OrderBuilder()

        # Set defaults
        symbol = kwargs.get("symbol", "AAPL")
        side = kwargs.get("side", "BUY")
        order_type = kwargs.get("order_type", "MARKET")
        quantity = kwargs.get("quantity", 100)

        builder.symbol(symbol)

        if side.upper() == "BUY":
            builder.buy()
        else:
            builder.sell()

        if order_type.upper() == "MARKET":
            builder.market()
        elif order_type.upper() == "LIMIT":
            price = kwargs.get("price", 150.00)
            builder.limit(price)
        elif order_type.upper() == "STOP":
            price = kwargs.get("price", 145.00)
            builder.stop(price)
        elif order_type.upper() == "STOP_LIMIT":
            stop_price = kwargs.get("stop_price", 145.00)
            limit_price = kwargs.get("limit_price", 146.00)
            builder.stop_limit(stop_price, limit_price)

        builder.quantity(quantity)

        return builder.build()
