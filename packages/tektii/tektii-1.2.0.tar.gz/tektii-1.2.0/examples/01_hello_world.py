"""Hello World Strategy Example.

This is a simple example demonstrating the basic structure of a Tektii strategy.
It logs market data events and demonstrates how to structure a trading strategy.
"""

import time
from decimal import Decimal
from typing import Optional

from tektii.strategy import TektiiStrategy
from tektii.strategy.models import BarData, OrderStatus, OrderUpdateEvent, TickData
from tektii.strategy.models.market_data import TickType


class HelloWorldStrategy(TektiiStrategy):
    """A simple strategy that demonstrates basic Tektii SDK functionality."""

    def __init__(self) -> None:
        """Initialize the HelloWorldStrategy."""
        super().__init__()
        self.tick_count = 0
        self.bar_count = 0

    def on_market_data(self, tick_data: Optional[TickData] = None, bar_data: Optional[BarData] = None) -> None:
        """Handle incoming market data events.

        This method is called whenever new market data is received.
        Either tick_data or bar_data will be provided, not both.
        """
        if tick_data:
            self.tick_count += 1
            print(f"[Tick #{self.tick_count}] {tick_data.symbol}: " f"Last=${tick_data.last}, Bid=${tick_data.bid}, Ask=${tick_data.ask}")

            # Example logic: Log when price crosses certain thresholds
            if tick_data.last is not None and tick_data.last < Decimal("100"):
                print("  → Price below $100 threshold!")
            elif tick_data.last is not None and tick_data.last > Decimal("200"):
                print("  → Price above $200 threshold!")

        elif bar_data:
            self.bar_count += 1
            print(
                f"[Bar #{self.bar_count}] {bar_data.symbol}: "
                f"Open=${bar_data.open}, High=${bar_data.high}, "
                f"Low=${bar_data.low}, Close=${bar_data.close}, Volume={bar_data.volume}"
            )

    def on_order_update(self, order_update: OrderUpdateEvent) -> None:
        """Handle order update events.

        This method is called whenever an order status changes.
        """
        print(f"Order Update: {order_update.order_id} is now {order_update.status}")

        if order_update.status == OrderStatus.FILLED:
            print(f"  → Order filled: {order_update.filled_quantity} @ ${order_update.avg_fill_price}")
        elif order_update.status == OrderStatus.REJECTED:
            print(f"  → Order rejected: {order_update.reject_reason}")

    def on_initialize(self, config: dict[str, str], symbols: list[str]) -> None:
        """Initialize the strategy with configuration.

        This is where you can set up initial state based on configuration.
        """
        print("Hello World Strategy initialized!")
        print(f"  Config: {config}")
        print(f"  Symbols: {symbols}")

    def on_shutdown(self) -> None:
        """Shut down the strategy."""
        print("Hello World Strategy shutting down.")
        print(f"  Processed {self.tick_count} ticks and {self.bar_count} bars")


if __name__ == "__main__":
    # This allows the strategy to be run directly for testing
    strategy = HelloWorldStrategy()
    print(f"Created {strategy.__class__.__name__} successfully!")

    # Simulate some market data
    test_tick = TickData(
        symbol="AAPL",
        timestamp_us=int(time.time() * 1_000_000),
        last=Decimal("150.25"),
        bid=Decimal("150.20"),
        ask=Decimal("150.30"),
        last_size=100,
        bid_size=500,
        ask_size=300,
        volume=10000,
        condition=None,
        mid=None,
        exchange=None,
        tick_type=TickType.QUOTE_AND_TRADE,
    )

    print("\nSimulating market data:")
    strategy.on_market_data(tick_data=test_tick)
