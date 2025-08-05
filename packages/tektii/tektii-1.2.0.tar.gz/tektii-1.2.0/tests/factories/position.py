"""Position test factories."""

from decimal import Decimal

import factory

from tektii.strategy.models.common import Position


class PositionFactory(factory.Factory):
    """Factory for creating test positions."""

    class Meta:
        model = Position

    symbol = factory.Faker("random_element", elements=["AAPL", "GOOGL", "MSFT", "SPY", "QQQ"])
    quantity = factory.LazyFunction(lambda: Decimal(factory.Faker._get_faker().pyint(min_value=-1000, max_value=1000)))
    avg_price = factory.LazyFunction(lambda: Decimal(factory.Faker._get_faker().pydecimal(left_digits=3, right_digits=2, positive=True)))
    market_value = factory.LazyAttribute(lambda obj: abs(obj.quantity) * obj.avg_price)
    realized_pnl = factory.LazyFunction(lambda: Decimal(factory.Faker._get_faker().pydecimal(left_digits=4, right_digits=2)))
    unrealized_pnl = factory.LazyFunction(lambda: Decimal(factory.Faker._get_faker().pydecimal(left_digits=4, right_digits=2)))
    current_price = factory.LazyAttribute(lambda obj: obj.avg_price + (obj.unrealized_pnl / abs(obj.quantity) if obj.quantity != 0 else Decimal("0")))

    @classmethod
    def create_long(cls, symbol="AAPL", quantity=100, avg_price=None, **kwargs):
        """Create a long position."""
        if avg_price is None:
            avg_price = Decimal("150.00")
        return cls(symbol=symbol, quantity=Decimal(str(abs(quantity))), avg_price=avg_price, **kwargs)  # Ensure positive

    @classmethod
    def create_short(cls, symbol="AAPL", quantity=100, average_price=None, **kwargs):
        """Create a short position."""
        if average_price is None:
            average_price = Decimal("150.00")
        return cls(symbol=symbol, quantity=Decimal(str(-abs(quantity))), avg_price=average_price, **kwargs)  # Ensure negative

    @classmethod
    def create_flat(cls, symbol="AAPL", **kwargs):
        """Create a flat (zero quantity) position."""
        return cls(symbol=symbol, quantity=Decimal("0"), **kwargs)
