"""Market data test factories."""

import time
from datetime import date, timedelta
from decimal import Decimal

import factory

from tektii.strategy.models.enums import OptionType
from tektii.strategy.models.market_data import BarData, OptionGreeks, TickData


class TickDataFactory(factory.Factory):
    """Factory for creating test tick data."""

    class Meta:
        model = TickData

    symbol = factory.Faker("random_element", elements=["AAPL", "GOOGL", "MSFT", "SPY", "QQQ"])
    timestamp_us = factory.LazyFunction(lambda: int(time.time() * 1_000_000))
    last = factory.LazyFunction(lambda: Decimal("150.25"))
    bid = factory.LazyAttribute(lambda obj: obj.last - Decimal("0.01"))
    ask = factory.LazyAttribute(lambda obj: obj.last + Decimal("0.01"))
    bid_size = factory.Faker("pyint", min_value=100, max_value=10000)
    ask_size = factory.Faker("pyint", min_value=100, max_value=10000)
    volume = factory.Faker("pyint", min_value=1000, max_value=1000000)
    condition = None

    @factory.post_generation
    def validate_spread(obj, create, extracted, **kwargs):
        """Ensure bid < ask."""
        if obj.bid >= obj.ask:
            obj.bid = obj.ask - Decimal("0.01")


class BarDataFactory(factory.Factory):
    """Factory for creating test bar data."""

    class Meta:
        model = BarData

    symbol = factory.Faker("random_element", elements=["AAPL", "GOOGL", "MSFT", "SPY", "QQQ"])
    timestamp_us = factory.LazyFunction(lambda: int(time.time() * 1_000_000))
    open = factory.LazyFunction(lambda: Decimal("100.00"))
    high = factory.LazyAttribute(lambda obj: obj.open + Decimal("5.00"))
    low = factory.LazyAttribute(lambda obj: obj.open - Decimal("5.00"))
    close = factory.LazyAttribute(lambda obj: obj.open + Decimal("2.50"))
    volume = factory.Faker("pyint", min_value=10000, max_value=10000000)
    vwap = factory.LazyAttribute(lambda obj: (obj.high + obj.low + obj.close) / 3)
    trade_count = factory.Faker("pyint", min_value=100, max_value=10000)
    bar_size = factory.Faker("random_element", elements=[1, 5, 15, 30, 60])
    bar_size_unit = factory.Faker("random_element", elements=["min", "hour", "day"])

    @factory.post_generation
    def validate_ohlc(obj, create, extracted, **kwargs):
        """Ensure OHLC relationships are valid."""
        # Ensure low <= open, close <= high
        if obj.low > obj.open:
            obj.low = obj.open - Decimal("1.00")
        if obj.low > obj.close:
            obj.low = min(obj.open, obj.close) - Decimal("1.00")
        if obj.high < obj.open:
            obj.high = obj.open + Decimal("1.00")
        if obj.high < obj.close:
            obj.high = max(obj.open, obj.close) + Decimal("1.00")


class OptionGreeksFactory(factory.Factory):
    """Factory for creating test option greeks."""

    class Meta:
        model = OptionGreeks

    symbol = factory.LazyAttribute(lambda obj: f"{obj.underlying}_{'C' if obj.option_type == OptionType.CALL else 'P'}{int(obj.strike)}")
    underlying = factory.Faker("random_element", elements=["AAPL", "GOOGL", "MSFT", "SPY", "QQQ"])
    option_type = factory.Faker("random_element", elements=[OptionType.CALL, OptionType.PUT])
    strike = factory.LazyFunction(lambda: Decimal("150.00"))
    expiration = factory.LazyFunction(lambda: date.today() + timedelta(days=30))

    # Greeks - adjust based on option type
    delta = factory.LazyAttribute(lambda obj: Decimal("0.50") if obj.option_type == OptionType.CALL else Decimal("-0.50"))
    gamma = factory.LazyFunction(lambda: Decimal("0.02"))
    theta = factory.LazyFunction(lambda: Decimal("-0.05"))
    vega = factory.LazyFunction(lambda: Decimal("0.15"))
    rho = factory.LazyFunction(lambda: Decimal("0.08"))

    # Pricing
    underlying_price = factory.LazyFunction(lambda: Decimal("152.50"))
    implied_volatility = factory.LazyFunction(lambda: Decimal("0.25"))
    theoretical_value = factory.LazyFunction(lambda: Decimal("5.75"))
    interest_rate = factory.LazyFunction(lambda: Decimal("0.05"))
    days_to_expiry = factory.LazyFunction(lambda: 30)
