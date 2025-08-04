#!/usr/bin/env python3
"""Example 02: Order Management and Event Handling Demo.

This example demonstrates the various event handling capabilities
available in the Tektii SDK, including:
- Market data handling (ticks and bars)
- Order update events
- Position update events
- Account update events
- Trade events
- System events
"""

from decimal import Decimal
from typing import Dict, List, Optional

from tektii.strategy import TektiiStrategy
from tektii.strategy.models import (
    AccountUpdateEvent,
    BarData,
    OrderSide,
    OrderStatus,
    OrderUpdateEvent,
    PositionUpdateEvent,
    SystemEvent,
    TickData,
    TradeEvent,
)


class EventHandlingDemo(TektiiStrategy):
    """Demonstrates event handling capabilities."""

    def __init__(self) -> None:
        """Initialize the strategy."""
        super().__init__()
        self.tick_count = 0
        self.bar_count = 0
        self.order_count = 0
        self.position_count = 0
        self.trade_count = 0
        self.last_tick_price: Optional[Decimal] = None
        self.last_bar_close: Optional[Decimal] = None

    def on_initialize(self, config: Dict[str, str], symbols: List[str]) -> None:
        """Initialize strategy with configuration and symbols.

        This method is called once when the strategy starts.
        """
        print("\n=== Strategy Initialization ===")
        print(f"Config: {config}")
        print(f"Symbols: {symbols}")

        # Store configuration
        self.threshold = Decimal(config.get("threshold", "100"))
        self.stop_loss_pct = Decimal(config.get("stop_loss_pct", "2.0"))
        self.take_profit_pct = Decimal(config.get("take_profit_pct", "5.0"))

        print(f"Threshold: ${self.threshold}")
        print(f"Stop Loss: {self.stop_loss_pct}%")
        print(f"Take Profit: {self.take_profit_pct}%")

    def on_market_data(self, tick_data: Optional[TickData] = None, bar_data: Optional[BarData] = None) -> None:
        """Handle incoming market data events.

        Either tick_data or bar_data will be provided, not both.
        """
        if tick_data:
            self._handle_tick_data(tick_data)
        elif bar_data:
            self._handle_bar_data(bar_data)

    def _handle_tick_data(self, tick: TickData) -> None:
        """Process tick data."""
        self.tick_count += 1
        self.last_tick_price = tick.last

        # Log every 10th tick to avoid spam
        if self.tick_count % 10 == 0:
            print(f"\n=== Tick #{self.tick_count} ===")
            print(f"Symbol: {tick.symbol}")
            if tick.last:
                print(f"Last: ${tick.last}")
            if tick.bid and tick.bid_size:
                print(f"Bid: ${tick.bid} x {tick.bid_size}")
            if tick.ask and tick.ask_size:
                print(f"Ask: ${tick.ask} x {tick.ask_size}")

            # Show spread analysis
            if tick.bid and tick.ask:
                spread = tick.ask - tick.bid
                if tick.last and tick.last > 0:
                    spread_pct = (spread / tick.last) * 100
                    print(f"Spread: ${spread} ({spread_pct:.3f}%)")

            # Exchange info if available
            if tick.exchange:
                print(f"Exchange: {tick.exchange}")

    def _handle_bar_data(self, bar: BarData) -> None:
        """Process bar data."""
        self.bar_count += 1
        self.last_bar_close = bar.close

        print(f"\n=== Bar #{self.bar_count} ===")
        print(f"Symbol: {bar.symbol}")
        print(f"Open: ${bar.open}")
        print(f"High: ${bar.high}")
        print(f"Low: ${bar.low}")
        print(f"Close: ${bar.close}")
        print(f"Volume: {bar.volume:,}")

        # Calculate bar statistics
        bar_range = bar.high - bar.low
        bar_change = bar.close - bar.open
        bar_change_pct = (bar_change / bar.open) * 100 if bar.open else 0

        print(f"Range: ${bar_range}")
        print(f"Change: ${bar_change} ({bar_change_pct:+.2f}%)")

        # VWAP if available
        if bar.vwap:
            print(f"VWAP: ${bar.vwap}")
            vwap_diff = bar.close - bar.vwap
            print(f"Close vs VWAP: ${vwap_diff:+.2f}")

    def on_order_update(self, order_update: OrderUpdateEvent) -> None:
        """Handle order update events."""
        self.order_count += 1

        print(f"\n=== Order Update #{self.order_count} ===")
        print(f"Order ID: {order_update.order_id}")
        print(f"Symbol: {order_update.symbol}")
        print(f"Status: {order_update.status.value}")
        print(f"Side: {order_update.side.value}")
        print(f"Type: {order_update.order_type.value}")
        print(f"Quantity: {order_update.quantity}")
        print(f"Filled: {order_update.filled_quantity}")
        print(f"Remaining: {order_update.remaining_quantity}")

        # Price information
        if order_update.limit_price:
            print(f"Limit Price: ${order_update.limit_price}")
        if order_update.stop_price:
            print(f"Stop Price: ${order_update.stop_price}")
        if order_update.avg_fill_price:
            print(f"Avg Fill Price: ${order_update.avg_fill_price}")

        # Rejection reason if rejected
        if order_update.status == OrderStatus.REJECTED and order_update.reject_reason:
            print(f"Reject Reason: {order_update.reject_reason}")

        # Calculate fill percentage
        if order_update.quantity > 0:
            fill_pct = (order_update.filled_quantity / order_update.quantity) * 100
            print(f"Fill %: {fill_pct:.1f}%")

    def on_position_update(self, position_update: PositionUpdateEvent) -> None:
        """Handle position update events."""
        self.position_count += 1

        print(f"\n=== Position Update #{self.position_count} ===")
        print(f"Symbol: {position_update.symbol}")
        print(f"Quantity: {position_update.quantity}")
        print(f"Avg Entry Price: ${position_update.avg_price}")

        # P&L information
        if position_update.unrealized_pnl is not None:
            print(f"Unrealized P&L: ${position_update.unrealized_pnl:+.2f}")
        if position_update.realized_pnl is not None:
            print(f"Realized P&L: ${position_update.realized_pnl:+.2f}")

        # Current market value and price
        if position_update.market_value:
            print(f"Market Value: ${position_update.market_value}")
        if position_update.current_price:
            print(f"Current Price: ${position_update.current_price}")

    def on_account_update(self, account_update: AccountUpdateEvent) -> None:
        """Handle account update events."""
        print("\n=== Account Update ===")
        print(f"Cash Balance: ${account_update.cash_balance}")
        print(f"Buying Power: ${account_update.buying_power}")

        # Margin information
        if account_update.margin_used:
            print(f"Margin Used: ${account_update.margin_used}")

    def on_trade(self, trade: TradeEvent) -> None:
        """Handle trade execution events."""
        self.trade_count += 1

        print(f"\n=== Trade Execution #{self.trade_count} ===")
        print(f"Trade ID: {trade.trade_id}")
        print(f"Order ID: {trade.order_id}")
        print(f"Symbol: {trade.symbol}")
        print(f"Side: {trade.side.value}")
        print(f"Quantity: {trade.quantity}")
        print(f"Price: ${trade.price}")
        print(f"Commission: ${trade.commission}")

        # Calculate trade value
        trade_value = trade.quantity * trade.price
        print(f"Trade Value: ${trade_value}")

        # Net value after commission
        if trade.side == OrderSide.BUY:
            net_value = trade_value + trade.commission
        else:
            net_value = trade_value - trade.commission
        print(f"Net Value: ${net_value}")

    def on_system_event(self, system_event: SystemEvent) -> None:
        """Handle system events."""
        print("\n=== System Event ===")
        print(f"Type: {system_event.type.value}")
        print(f"Message: {system_event.message}")

        # Show details if provided
        if system_event.details:
            print("Details:")
            for key, value in system_event.details.items():
                print(f"  {key}: {value}")

    def on_error(self, error: Exception) -> None:
        """Handle errors during strategy execution."""
        print("\n=== Error ===")
        print(f"Error Type: {type(error).__name__}")
        print(f"Error Message: {error}")

    def on_shutdown(self) -> None:
        """Clean up when strategy is shutting down."""
        print("\n=== Strategy Shutdown ===")
        print(f"Total ticks processed: {self.tick_count}")
        print(f"Total bars processed: {self.bar_count}")
        print(f"Total order updates: {self.order_count}")
        print(f"Total position updates: {self.position_count}")
        print(f"Total trades: {self.trade_count}")

        if self.last_tick_price:
            print(f"Last tick price: ${self.last_tick_price}")
        if self.last_bar_close:
            print(f"Last bar close: ${self.last_bar_close}")


# Entry point for direct execution
if __name__ == "__main__":
    strategy = EventHandlingDemo()
    print("Event Handling Demo Strategy initialized")
    print("This strategy demonstrates handling of:")
    print("- Market data (ticks and bars)")
    print("- Order updates")
    print("- Position updates")
    print("- Account updates")
    print("- Trade executions")
    print("- System events")
