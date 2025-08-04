"""Event test factories."""

import time
from decimal import Decimal

import factory

from tektii.strategy.models.enums import OrderSide, OrderStatus, OrderType
from tektii.strategy.models.errors import SystemEventType
from tektii.strategy.models.events import AccountUpdateEvent, OrderUpdateEvent, PositionUpdateEvent, SystemEvent, TradeEvent

from .market_data import TickDataFactory


class OrderUpdateEventFactory(factory.Factory):
    """Factory for creating test order update events."""

    class Meta:
        model = OrderUpdateEvent

    order_id = factory.Faker("uuid4")
    symbol = factory.Faker("random_element", elements=["AAPL", "GOOGL", "MSFT", "SPY", "QQQ"])
    status = factory.Faker("random_element", elements=list(OrderStatus))
    side = factory.Faker("random_element", elements=[OrderSide.BUY, OrderSide.SELL])
    order_type = factory.Faker("random_element", elements=list(OrderType))
    quantity = factory.LazyFunction(lambda: Decimal(factory.Faker._get_faker().pyint(min_value=1, max_value=1000)))
    filled_quantity = factory.LazyAttribute(
        lambda obj: min(obj.quantity, Decimal(factory.Faker._get_faker().pyint(min_value=0, max_value=int(obj.quantity))))
    )
    remaining_quantity = factory.LazyAttribute(lambda obj: obj.quantity - obj.filled_quantity)
    limit_price = factory.LazyFunction(lambda: Decimal(factory.Faker._get_faker().pydecimal(left_digits=3, right_digits=2, positive=True)))
    stop_price = None
    avg_fill_price = factory.LazyAttribute(lambda obj: obj.limit_price if obj.filled_quantity > 0 else None)
    created_at_us = factory.LazyFunction(lambda: int(time.time() * 1_000_000))
    updated_at_us = factory.LazyAttribute(lambda obj: obj.created_at_us + factory.Faker._get_faker().pyint(min_value=1000, max_value=60000000))
    reject_reason = None
    metadata = factory.Dict({})


class PositionUpdateEventFactory(factory.Factory):
    """Factory for creating test position update events."""

    class Meta:
        model = PositionUpdateEvent

    symbol = factory.Faker("random_element", elements=["AAPL", "GOOGL", "MSFT", "SPY", "QQQ"])
    quantity = factory.LazyFunction(lambda: Decimal(factory.Faker._get_faker().pyint(min_value=-1000, max_value=1000)))
    avg_price = factory.LazyFunction(lambda: Decimal(factory.Faker._get_faker().pydecimal(left_digits=3, right_digits=2, positive=True)))
    unrealized_pnl = factory.LazyFunction(lambda: Decimal(factory.Faker._get_faker().pydecimal(left_digits=4, right_digits=2, positive=False)))
    realized_pnl = factory.LazyFunction(lambda: Decimal(factory.Faker._get_faker().pydecimal(left_digits=4, right_digits=2, positive=False)))
    market_value = factory.LazyAttribute(lambda obj: abs(obj.quantity) * obj.avg_price)
    current_price = factory.LazyAttribute(lambda obj: obj.avg_price + (obj.unrealized_pnl / abs(obj.quantity) if obj.quantity != 0 else Decimal("0")))
    bid = factory.LazyAttribute(lambda obj: obj.current_price - Decimal("0.01") if obj.current_price else None)
    ask = factory.LazyAttribute(lambda obj: obj.current_price + Decimal("0.01") if obj.current_price else None)


class AccountUpdateEventFactory(factory.Factory):
    """Factory for creating test account update events."""

    class Meta:
        model = AccountUpdateEvent

    cash_balance = factory.LazyFunction(lambda: Decimal(factory.Faker._get_faker().pydecimal(left_digits=6, right_digits=2, positive=True)))
    portfolio_value = factory.LazyAttribute(
        lambda obj: obj.cash_balance + Decimal(factory.Faker._get_faker().pydecimal(left_digits=5, right_digits=2, positive=True))
    )
    buying_power = factory.LazyAttribute(lambda obj: obj.cash_balance * 4)
    initial_margin = factory.LazyFunction(lambda: Decimal(factory.Faker._get_faker().pydecimal(left_digits=5, right_digits=2, positive=True)))
    maintenance_margin = factory.LazyAttribute(lambda obj: obj.initial_margin * Decimal("0.75"))
    margin_used = factory.LazyAttribute(
        lambda obj: obj.initial_margin * Decimal(factory.Faker._get_faker().pydecimal(left_digits=0, right_digits=2, positive=True, max_value=1))
    )
    daily_pnl = factory.LazyFunction(lambda: Decimal(factory.Faker._get_faker().pydecimal(left_digits=4, right_digits=2, positive=False)))
    total_pnl = factory.LazyFunction(lambda: Decimal(factory.Faker._get_faker().pydecimal(left_digits=5, right_digits=2, positive=False)))
    leverage = factory.LazyFunction(lambda: Decimal(factory.Faker._get_faker().pydecimal(left_digits=1, right_digits=2, positive=True, max_value=4)))
    risk_metrics = factory.Dict({})


class TradeEventFactory(factory.Factory):
    """Factory for creating test trade events."""

    class Meta:
        model = TradeEvent

    trade_id = factory.Faker("uuid4")
    order_id = factory.Faker("uuid4")
    symbol = factory.Faker("random_element", elements=["AAPL", "GOOGL", "MSFT", "SPY", "QQQ"])
    side = factory.Faker("random_element", elements=[OrderSide.BUY, OrderSide.SELL])
    quantity = factory.LazyFunction(lambda: Decimal(factory.Faker._get_faker().pyint(min_value=1, max_value=1000)))
    price = factory.LazyFunction(lambda: Decimal(factory.Faker._get_faker().pydecimal(left_digits=3, right_digits=2, positive=True)))
    timestamp_us = factory.LazyFunction(lambda: int(time.time() * 1_000_000))
    commission = factory.LazyFunction(
        lambda: Decimal(factory.Faker._get_faker().pydecimal(left_digits=1, right_digits=2, positive=True, max_value=10))
    )
    fees = factory.LazyFunction(lambda: Decimal(factory.Faker._get_faker().pydecimal(left_digits=1, right_digits=2, positive=True, max_value=5)))


class SystemEventFactory(factory.Factory):
    """Factory for creating test system events."""

    class Meta:
        model = SystemEvent

    type = factory.Faker("random_element", elements=list(SystemEventType))
    message = factory.Faker("sentence", nb_words=6)
    details = factory.Dict({})


# Legacy compatibility aliases
ErrorEventFactory = SystemEventFactory
MarketDataEventFactory = TickDataFactory
