"""Enhanced mock broker with realistic market behavior.

This module provides an enhanced version of the mock broker that simulates
realistic market conditions including partial fills, slippage, and rejections.
"""

from __future__ import annotations

import threading
import time
from decimal import Decimal
from typing import Optional

import grpc

from tektii.strategy.grpc import common_pb2, orders_pb2
from tektii.testing.market_simulator import MarketCondition, RealisticMarketSimulator
from tektii.testing.mock_broker import MockBrokerService


class RealisticMockBroker(MockBrokerService):
    """Enhanced mock broker with realistic market simulation."""

    def __init__(self, initial_cash: Optional[Decimal] = None) -> None:
        """Initialize the realistic broker.

        Args:
            initial_cash: Starting cash balance (defaults to 100000)
        """
        super().__init__()
        if initial_cash is None:
            initial_cash = Decimal("100000")

        # Initialize market simulator
        self.market_sim = RealisticMarketSimulator()

        # Order execution settings
        self.enable_partial_fills = True
        self.enable_slippage = True
        self.enable_rejections = True

        # Background market updates
        self._market_update_thread: Optional[threading.Thread] = None
        self._stop_market_updates = threading.Event()

        # Set initial cash
        self.account.cash_balance = float(initial_cash)
        self.account.portfolio_value = float(initial_cash)
        self.account.buying_power = float(initial_cash)

    def start_market_simulation(self, update_interval: float = 1.0) -> None:
        """Start background market price updates.

        Args:
            update_interval: Seconds between market updates
        """
        self._stop_market_updates.clear()

        def update_markets() -> None:
            while not self._stop_market_updates.is_set():
                self.market_sim.update_all_markets(update_interval)
                self._update_position_values()
                time.sleep(update_interval)

        self._market_update_thread = threading.Thread(target=update_markets)
        self._market_update_thread.start()

    def stop_market_simulation(self) -> None:
        """Stop background market updates."""
        if self._market_update_thread:
            self._stop_market_updates.set()
            self._market_update_thread.join()
            self._market_update_thread = None

    def _update_position_values(self) -> None:
        """Update position market values based on current prices."""
        total_value = Decimal(str(self.account.cash_balance))

        for symbol, position in self.positions.items():
            if symbol in self.market_sim.markets:
                market = self.market_sim.markets[symbol]
                position.current_price = float(market.last_price)
                position.market_value = float(Decimal(str(position.quantity)) * market.last_price)

                # Calculate unrealized P&L
                cost_basis = Decimal(str(position.quantity)) * Decimal(str(position.avg_price))
                current_value = Decimal(str(position.market_value))
                position.unrealized_pnl = float(current_value - cost_basis)

                total_value += current_value

        self.account.portfolio_value = float(total_value)

        # Simple margin calculation
        margin_used = sum(abs(p.market_value) * 0.5 for p in self.positions.values())  # 50% margin requirement
        self.account.margin_used = margin_used
        self.account.buying_power = self.account.cash_balance - margin_used

    def PlaceOrder(self, request: orders_pb2.PlaceOrderRequest, context: grpc.ServicerContext) -> orders_pb2.PlaceOrderResponse:
        """Place order with realistic execution simulation."""
        response = orders_pb2.PlaceOrderResponse()

        # Check for rejections
        if self.enable_rejections:
            should_reject, reason = self.market_sim.should_reject_order(
                request.symbol, request.order_type, Decimal(str(request.limit_price)) if request.limit_price else None
            )
            if should_reject:
                response.accepted = False
                response.reject_reason = reason
                response.reject_code = common_pb2.REJECT_CODE_MARKET_CLOSED
                return response

        # Basic validation
        if request.quantity <= 0:
            response.accepted = False
            response.reject_reason = "Invalid quantity"
            response.reject_code = common_pb2.REJECT_CODE_INVALID_QUANTITY
            return response

        # Risk checks
        if not self._check_risk_limits(request):
            response.accepted = False
            response.reject_reason = "Risk limit exceeded"
            response.reject_code = common_pb2.REJECT_CODE_RISK_CHECK_FAILED
            response.risk_check.position_limit = 10000
            response.risk_check.current_position = abs(self.positions[request.symbol].quantity) if request.symbol in self.positions else 0
            response.risk_check.resulting_position = response.risk_check.current_position + request.quantity
            return response

        # Generate order ID
        self.order_counter += 1
        order_id = f"TEST-{self.order_counter:06d}"

        # Get execution price
        exec_price = self.market_sim.get_execution_price(
            request.symbol,
            request.side,
            Decimal(str(request.quantity)),
            request.order_type,
            Decimal(str(request.limit_price)) if request.limit_price else None,
        )

        if exec_price is None:
            # Limit order goes on book
            order_status = common_pb2.ORDER_STATUS_SUBMITTED
        else:
            # Immediate execution
            order_status = common_pb2.ORDER_STATUS_FILLED

        # Create order
        order = common_pb2.Order(
            order_id=order_id,
            symbol=request.symbol,
            status=order_status,
            side=request.side,
            order_type=request.order_type,
            quantity=request.quantity,
            filled_quantity=request.quantity if exec_price else 0.0,
            limit_price=request.limit_price,
            stop_price=request.stop_price,
            created_at_us=int(time.time() * 1_000_000),
            order_intent=request.order_intent,
            parent_trade_id=request.parent_trade_id,
        )

        self.orders[order_id] = order

        # Handle immediate execution
        if exec_price:
            self._execute_order(order, exec_price)

        # Success response
        response.accepted = True
        response.order_id = order_id
        response.request_id = request.request_id
        response.timestamp_us = int(time.time() * 1_000_000)
        response.estimated_fill_price = (
            float(exec_price)
            if exec_price
            else float(self.market_sim.markets[request.symbol].last_price if request.symbol in self.market_sim.markets else 100.0)
        )
        response.estimated_commission = 1.0
        # Set risk check values (no 'passed' field)
        response.risk_check.buying_power_remaining = self.account.buying_power

        return response

    def _check_risk_limits(self, request: orders_pb2.PlaceOrderRequest) -> bool:
        """Check if order passes risk limits.

        Args:
            request: Order request to validate

        Returns:
            True if order passes risk checks
        """
        # Position limits
        if request.symbol in self.positions:
            current_pos = abs(self.positions[request.symbol].quantity)
            new_pos = current_pos + request.quantity
            if new_pos > 10000:  # Max position size
                return False
        else:
            # Check new position size
            if request.quantity > 10000:
                return False

        # Buying power check - only for buy orders
        if request.side == common_pb2.ORDER_SIDE_BUY and request.symbol in self.market_sim.markets:
            market = self.market_sim.markets[request.symbol]
            order_value = float(market.ask * Decimal(str(request.quantity)))
            if order_value > self.account.buying_power:
                return False

        return True

    def _execute_order(self, order: common_pb2.Order, price: Decimal) -> None:
        """Execute an order at the given price.

        Args:
            order: Order to execute
            price: Execution price
        """
        # Handle partial fills
        if self.enable_partial_fills and order.quantity > 1000:
            # Simulate partial fills but for now just do a single fill
            order.filled_quantity = order.quantity
        else:
            order.filled_quantity = order.quantity

        order.status = common_pb2.ORDER_STATUS_FILLED

        # Update position
        if order.symbol not in self.positions:
            self.positions[order.symbol] = common_pb2.Position(
                symbol=order.symbol,
                quantity=0.0,
                avg_price=0.0,
                market_value=0.0,
                unrealized_pnl=0.0,
                realized_pnl=0.0,
                current_price=float(price),
            )

        position = self.positions[order.symbol]
        old_quantity = Decimal(str(position.quantity))
        old_avg_price = Decimal(str(position.avg_price))
        fill_quantity = Decimal(str(order.filled_quantity))

        if order.side == common_pb2.ORDER_SIDE_BUY:
            # Update position for buy
            new_quantity = old_quantity + fill_quantity
            if new_quantity != 0:
                # Calculate new average price
                old_value = old_quantity * old_avg_price
                new_value = fill_quantity * price
                position.avg_price = float((old_value + new_value) / new_quantity)
            position.quantity = float(new_quantity)
        else:
            # Update position for sell
            new_quantity = old_quantity - fill_quantity

            # Calculate realized P&L
            if old_quantity > 0:  # Closing long position
                realized_pnl = fill_quantity * (price - old_avg_price)
                position.realized_pnl += float(realized_pnl)

            position.quantity = float(new_quantity)

            # Reset avg price if position closed
            if abs(new_quantity) < 0.0001:
                position.avg_price = 0.0

        # Update account cash
        trade_value = float(fill_quantity * price)
        commission = 1.0

        if order.side == common_pb2.ORDER_SIDE_BUY:
            self.account.cash_balance -= trade_value + commission
        else:
            self.account.cash_balance += trade_value - commission

        # Update position market value
        position.market_value = position.quantity * float(price)
        position.current_price = float(price)

        # Update account
        self._update_position_values()

    def SimulateMarketMovement(self, symbol: str, target_price: Decimal, steps: int = 10, interval: float = 0.1) -> None:
        """Simulate gradual price movement to target.

        Args:
            symbol: Symbol to move
            target_price: Target price to reach
            steps: Number of steps to take
            interval: Time between steps in seconds
        """
        if symbol not in self.market_sim.markets:
            return

        market = self.market_sim.markets[symbol]
        start_price = market.last_price
        price_diff = target_price - start_price

        for i in range(steps):
            progress = (i + 1) / steps
            new_price = start_price + (price_diff * Decimal(str(progress)))

            market.last_price = new_price
            market.bid = new_price - market.spread / 2
            market.ask = new_price + market.spread / 2

            self._update_position_values()
            time.sleep(interval)

    def SetMarketCondition(self, symbol: str, condition: MarketCondition) -> None:
        """Set market condition for a symbol.

        Args:
            symbol: Symbol to update
            condition: New market condition
        """
        if symbol in self.market_sim.markets:
            self.market_sim.markets[symbol].condition = condition
