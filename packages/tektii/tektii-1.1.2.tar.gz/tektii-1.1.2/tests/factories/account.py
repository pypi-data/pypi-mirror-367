"""Account test factories."""

from decimal import Decimal

import factory

from tektii.strategy.models.common import AccountState


class AccountStateFactory(factory.Factory):
    """Factory for creating test account states."""

    class Meta:
        model = AccountState

    cash_balance = factory.LazyFunction(lambda: Decimal(factory.Faker._get_faker().pydecimal(left_digits=6, right_digits=2, positive=True)))
    portfolio_value = factory.LazyAttribute(lambda obj: obj.cash_balance)
    buying_power = factory.LazyAttribute(lambda obj: obj.cash_balance * Decimal("4"))  # 4x leverage
    initial_margin = factory.LazyFunction(lambda: Decimal(factory.Faker._get_faker().pydecimal(left_digits=5, right_digits=2, positive=True)))
    maintenance_margin = factory.LazyAttribute(lambda obj: obj.initial_margin * Decimal("0.75"))
    margin_used = factory.LazyAttribute(
        lambda obj: obj.initial_margin * Decimal(factory.Faker._get_faker().pydecimal(left_digits=0, right_digits=2, positive=True, max_value=1))
    )
    daily_pnl = factory.LazyFunction(lambda: Decimal(factory.Faker._get_faker().pydecimal(left_digits=4, right_digits=2)))
    total_pnl = factory.LazyFunction(lambda: Decimal(factory.Faker._get_faker().pydecimal(left_digits=5, right_digits=2)))

    @classmethod
    def create_with_balance(cls, balance):
        """Create account state with specific balance."""
        return cls(cash_balance=Decimal(str(balance)), portfolio_value=Decimal(str(balance)), buying_power=Decimal(str(balance)) * 4)


# Legacy compatibility alias
AccountFactory = AccountStateFactory
