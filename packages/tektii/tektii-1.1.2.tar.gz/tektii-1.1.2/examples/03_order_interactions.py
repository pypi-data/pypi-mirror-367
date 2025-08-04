#!/usr/bin/env python3
"""Example 03: Order Interactions Demo.

This example demonstrates all available order interaction capabilities:
- PlaceOrder: Submit new orders (market, limit, stop)
- CancelOrder: Cancel pending orders
- ModifyOrder: Modify existing orders (when available)
- ValidateOrder: Pre-validate orders before submission
- ClosePosition: Close existing positions
- ModifyTradeProtection: Adjust stop loss/take profit (when available)

This is a demonstration strategy focused on clear examples rather than
valid trading logic.
"""

from decimal import Decimal
from typing import Dict, List, Optional

from tektii.strategy import TektiiStrategy
from tektii.strategy.models import (
    BarData,
    CancelOrderRequest,
    ClosePositionRequest,
    OrderBuilder,
    OrderIntent,
    OrderSide,
    OrderStatus,
    OrderType,
    OrderUpdateEvent,
    PlaceOrderRequest,
    PositionUpdateEvent,
    TickData,
    TimeInForce,
    ValidateOrderRequest,
)


class OrderInteractionsDemo(TektiiStrategy):
    """Demonstrates all order interaction capabilities."""

    def __init__(self) -> None:
        """Initialize the strategy."""
        super().__init__()
        self.demo_phase = 0
        self.placed_orders: Dict[str, str] = {}  # symbol -> order_id
        self.last_price: Dict[str, Decimal] = {}  # symbol -> last price

    def on_initialize(self, config: Dict[str, str], symbols: List[str]) -> None:
        """Initialize strategy with configuration."""
        print("\n=== Order Interactions Demo ===")
        print(f"Symbols: {symbols}")
        print("\nThis demo will show:")
        print("1. Validating orders before placement")
        print("2. Placing various order types")
        print("3. Canceling orders")
        print("4. Closing positions")
        print("5. Using protective orders\n")

    def on_market_data(self, tick_data: Optional[TickData] = None, bar_data: Optional[BarData] = None) -> None:
        """Handle market data and demonstrate order interactions."""
        if not self._broker_stub:
            print("Note: Broker stub not available - order interactions shown as examples only")
            return

        # Track last prices
        if tick_data and tick_data.last:
            self.last_price[tick_data.symbol] = tick_data.last
            self._demonstrate_order_interactions(tick_data.symbol, tick_data.last)
        elif bar_data:
            self.last_price[bar_data.symbol] = bar_data.close
            self._demonstrate_order_interactions(bar_data.symbol, bar_data.close)

    def _demonstrate_order_interactions(self, symbol: str, price: Decimal) -> None:
        """Demonstrate different order interactions based on demo phase."""
        # Increment demo phase with each market update (for demonstration)
        self.demo_phase += 1

        if self.demo_phase == 1:
            print("\n=== Phase 1: Order Validation ===")
            self._demonstrate_order_validation(symbol, price)

        elif self.demo_phase == 5:
            print("\n=== Phase 2: Placing Orders ===")
            self._demonstrate_order_placement(symbol, price)

        elif self.demo_phase == 10:
            print("\n=== Phase 3: Canceling Orders ===")
            self._demonstrate_order_cancellation(symbol)

        elif self.demo_phase == 15:
            print("\n=== Phase 4: Closing Positions ===")
            self._demonstrate_position_closing(symbol, price)

        elif self.demo_phase == 20:
            print("\n=== Phase 5: Protective Orders ===")
            self._demonstrate_protective_orders(symbol, price)

    def _demonstrate_order_validation(self, symbol: str, price: Decimal) -> None:
        """Demonstrate pre-trade order validation."""
        print(f"Validating orders for {symbol} at ${price}")

        # Example 1: Validate a market buy order
        validation_request = ValidateOrderRequest(
            symbol=symbol,
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=Decimal("100"),
            limit_price=None,
            stop_price=None,
            request_id=None,
        )

        try:
            if self._broker_stub:
                response = self._broker_stub.ValidateOrder(validation_request.to_proto())
            else:
                return
            if response.valid:
                print("✓ Market buy order is valid")
                if response.estimated_fill_price:
                    print(f"  Estimated fill: ${response.estimated_fill_price}")
            else:
                print("✗ Market buy order validation failed")
                for error in response.errors:
                    print(f"  Error: {error.message}")
        except Exception as e:
            print(f"Validation error: {e}")

        # Example 2: Validate a limit order with invalid price
        limit_price = price * Decimal("0.5")  # 50% below market - might be rejected
        validation_request = ValidateOrderRequest(
            symbol=symbol,
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("100"),
            limit_price=limit_price,
            stop_price=None,
            request_id=None,
        )

        try:
            if self._broker_stub:
                response = self._broker_stub.ValidateOrder(validation_request.to_proto())
            else:
                return
            if response.valid:
                print(f"✓ Limit buy at ${limit_price} is valid")
            else:
                print(f"✗ Limit buy at ${limit_price} validation failed")
                for warning in response.warnings:
                    print(f"  Warning: {warning.message}")
        except Exception as e:
            print(f"Validation error: {e}")

    def _demonstrate_order_placement(self, symbol: str, price: Decimal) -> None:
        """Demonstrate placing various order types."""
        print(f"Placing orders for {symbol} at ${price}")

        # Example 1: Place a market order using OrderBuilder
        market_order = (
            OrderBuilder()
            .symbol(symbol)
            .buy()
            .market()
            .quantity(50)
            .time_in_force(TimeInForce.IOC)  # Immediate or cancel
            .metadata("demo_type", "market_order")
            .metadata("strategy_version", "1.0")
            .build()
        )

        try:
            if self._broker_stub:
                response = self._broker_stub.PlaceOrder(market_order)
            else:
                return
            if response.accepted:
                print(f"✓ Market order placed: {response.order_id}")
                self.placed_orders[symbol] = response.order_id
            else:
                print(f"✗ Market order rejected: {response.reject_reason}")
        except Exception as e:
            print(f"Order placement error: {e}")

        # Example 2: Place a limit order
        limit_price = price - Decimal("0.50")  # $0.50 below market
        limit_order = (
            OrderBuilder()
            .symbol(symbol)
            .buy()
            .limit(float(limit_price))
            .quantity(100)
            .time_in_force(TimeInForce.GTC)  # Good till canceled
            .client_order_id(f"demo_limit_{symbol}")
            .build()
        )

        try:
            if self._broker_stub:
                response = self._broker_stub.PlaceOrder(limit_order)
            else:
                return
            if response.accepted:
                print(f"✓ Limit order placed at ${limit_price}: {response.order_id}")
        except Exception as e:
            print(f"Order placement error: {e}")

        # Example 3: Place a stop loss order
        stop_price = price - Decimal("2.00")  # $2 below market
        stop_order = PlaceOrderRequest(
            symbol=symbol,
            side=OrderSide.SELL,
            order_type=OrderType.STOP,
            quantity=Decimal("50"),
            limit_price=None,
            stop_price=stop_price,
            time_in_force=TimeInForce.DAY,
            client_order_id=None,
            metadata={"order_purpose": "stop_loss", "trigger_price": str(stop_price)},
            order_intent=OrderIntent.UNKNOWN,
            parent_trade_id=None,
            protective_orders_on_fill=None,
            request_id=None,
            validate_only=False,
        )

        try:
            if self._broker_stub:
                response = self._broker_stub.PlaceOrder(stop_order.to_proto())
            else:
                return
            if response.accepted:
                print(f"✓ Stop loss placed at ${stop_price}: {response.order_id}")
        except Exception as e:
            print(f"Order placement error: {e}")

    def _demonstrate_order_cancellation(self, symbol: str) -> None:
        """Demonstrate canceling orders."""
        if symbol not in self.placed_orders:
            print(f"No orders to cancel for {symbol}")
            return

        order_id = self.placed_orders[symbol]
        print(f"Canceling order {order_id} for {symbol}")

        cancel_request = CancelOrderRequest(
            order_id=order_id,
            request_id=f"cancel_demo_{order_id}",
        )

        try:
            if self._broker_stub:
                response = self._broker_stub.CancelOrder(cancel_request.to_proto())
            else:
                return
            if response.accepted:
                print(f"✓ Order {order_id} canceled")
                if response.filled_quantity and response.filled_quantity > 0:
                    print(f"  Filled quantity before cancel: {response.filled_quantity}")
                del self.placed_orders[symbol]
            else:
                print(f"✗ Cancel rejected: {response.reject_reason}")
        except Exception as e:
            print(f"Cancel error: {e}")

    def _demonstrate_position_closing(self, symbol: str, price: Decimal) -> None:
        """Demonstrate closing positions."""
        # Check if we have a position
        if symbol not in self._positions or self._positions[symbol].quantity == 0:
            print(f"No position to close for {symbol}")
            return

        position = self._positions[symbol]
        print(f"Closing position: {position.quantity} shares of {symbol}")

        # Example 1: Close entire position at market
        close_request = ClosePositionRequest(
            symbol=symbol,
            quantity=Decimal(0),  # 0 means close entire position
            order_type=OrderType.MARKET,
            limit_price=None,
            request_id=None,
        )

        try:
            if self._broker_stub:
                response = self._broker_stub.ClosePosition(close_request.to_proto())
            else:
                return
            if response.accepted:
                print(f"✓ Position close order(s) placed: {response.order_ids}")
                print(f"  Closing {response.closing_quantity} of {response.position_quantity} shares")
            else:
                print(f"✗ Close rejected: {response.reject_reason}")
        except Exception as e:
            print(f"Close position error: {e}")

        # Example 2: Partial close with limit order
        if position.quantity > 100:
            limit_price = price + Decimal("0.10")  # Try to sell $0.10 above market
            partial_close = ClosePositionRequest(
                symbol=symbol,
                quantity=Decimal("50"),  # Close only 50 shares
                order_type=OrderType.LIMIT,
                limit_price=limit_price,
                request_id=None,
            )

            try:
                if self._broker_stub:
                    response = self._broker_stub.ClosePosition(partial_close.to_proto())
                else:
                    return
                if response.accepted:
                    print(f"✓ Partial close at ${limit_price}: {response.order_ids}")
            except Exception as e:
                print(f"Partial close error: {e}")

    def _demonstrate_protective_orders(self, symbol: str, price: Decimal) -> None:
        """Demonstrate orders with automatic protective orders on fill."""
        print(f"Placing order with protective orders for {symbol}")

        # Calculate stop loss and take profit levels
        stop_loss_price = price * Decimal("0.98")  # 2% stop loss
        take_profit_price = price * Decimal("1.05")  # 5% take profit

        # Place a buy order with protective orders that activate on fill
        order_with_protection = (
            OrderBuilder()
            .symbol(symbol)
            .buy()
            .market()
            .quantity(100)
            .with_stop_loss(float(stop_loss_price))
            .with_take_profit(float(take_profit_price))
            .metadata("strategy", "demo_protective")
            .build()
        )

        try:
            if self._broker_stub:
                response = self._broker_stub.PlaceOrder(order_with_protection)
            else:
                return
            if response.accepted:
                print(f"✓ Order with protection placed: {response.order_id}")
                print(f"  Stop loss will be at: ${stop_loss_price}")
                print(f"  Take profit will be at: ${take_profit_price}")
            else:
                print(f"✗ Order rejected: {response.reject_reason}")
        except Exception as e:
            print(f"Protected order error: {e}")

    def on_order_update(self, order_update: OrderUpdateEvent) -> None:
        """Handle order updates."""
        print(f"\n[Order Update] {order_update.order_id}: {order_update.status.value}")

        if order_update.status == OrderStatus.FILLED:
            print(f"  Filled: {order_update.filled_quantity} @ ${order_update.avg_fill_price}")
            # Track fills for demo purposes
            if order_update.metadata and "demo_type" in order_update.metadata:
                print(f"  Demo type: {order_update.metadata['demo_type']}")

        elif order_update.status == OrderStatus.PARTIAL:
            print(f"  Partial fill: {order_update.filled_quantity}/{order_update.quantity}")

        elif order_update.status == OrderStatus.CANCELED:
            print(f"  Canceled with {order_update.remaining_quantity} remaining")

        elif order_update.status == OrderStatus.REJECTED:
            print(f"  Rejection reason: {order_update.reject_reason}")

    def on_position_update(self, position_update: PositionUpdateEvent) -> None:
        """Handle position updates."""
        print(f"\n[Position Update] {position_update.symbol}: {position_update.quantity} shares")
        if position_update.unrealized_pnl:
            print(f"  Unrealized P&L: ${position_update.unrealized_pnl:+.2f}")

    def on_shutdown(self) -> None:
        """Clean up on shutdown."""
        print("\n=== Order Interactions Demo Complete ===")
        print(f"Demo phases completed: {self.demo_phase}")
        if self.placed_orders:
            print(f"Active orders: {len(self.placed_orders)}")


# Entry point for direct execution
if __name__ == "__main__":
    strategy = OrderInteractionsDemo()
    print("Order Interactions Demo Strategy initialized")
    print("\nThis strategy demonstrates:")
    print("- Order validation before submission")
    print("- Placing market, limit, and stop orders")
    print("- Canceling pending orders")
    print("- Closing positions (full and partial)")
    print("- Using protective orders (stop loss + take profit)")
    print("\nNote: This is a demonstration strategy focused on clear examples")
    print("rather than valid trading logic. In production, you would use")
    print("these capabilities based on your actual trading strategy.")
