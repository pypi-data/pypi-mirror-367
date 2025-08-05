"""Market simulation utilities for realistic testing.

This module provides tools for simulating realistic market behavior
including price movements, order book dynamics, and execution logic.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Tuple

from tektii.strategy.grpc import common_pb2


class MarketCondition(Enum):
    """Market conditions that affect price behavior."""

    NORMAL = "normal"
    VOLATILE = "volatile"
    TRENDING_UP = "trending_up"
    TRENDING_DOWN = "trending_down"
    RANGE_BOUND = "range_bound"


@dataclass
class MarketState:
    """Current state of a simulated market."""

    symbol: str
    last_price: Decimal
    bid: Decimal
    ask: Decimal
    volume: int = 0

    # Market microstructure
    spread: Decimal = Decimal("0.01")
    volatility: Decimal = Decimal("0.02")  # 2% daily volatility
    trend: Decimal = Decimal("0")  # Drift rate

    # Order book depth
    bid_depth: List[Tuple[Decimal, int]] = field(default_factory=list)
    ask_depth: List[Tuple[Decimal, int]] = field(default_factory=list)

    # Market condition
    condition: MarketCondition = MarketCondition.NORMAL

    def update_price(self, dt: float = 1.0) -> None:
        """Update market price based on random walk with drift.

        Args:
            dt: Time step in seconds
        """
        # Convert dt to fraction of trading day (6.5 hours)
        dt_fraction = Decimal(str(dt / (6.5 * 3600)))

        # Random walk with drift
        drift = self.trend * dt_fraction
        diffusion = self.volatility * Decimal(str(random.random() - 0.5)) * (dt_fraction ** Decimal("0.5"))

        # Apply market condition adjustments
        if self.condition == MarketCondition.VOLATILE:
            diffusion *= 2
        elif self.condition == MarketCondition.TRENDING_UP:
            drift += Decimal("0.001")
        elif self.condition == MarketCondition.TRENDING_DOWN:
            drift -= Decimal("0.001")

        # Update price
        price_change = self.last_price * (drift + diffusion)
        self.last_price += price_change

        # Update bid/ask
        half_spread = self.spread / 2
        self.bid = self.last_price - half_spread
        self.ask = self.last_price + half_spread

        # Add some randomness to spread
        if self.condition == MarketCondition.VOLATILE:
            spread_adjustment = Decimal(str(random.uniform(0.5, 2.0)))
            self.bid = self.last_price - (half_spread * spread_adjustment)
            self.ask = self.last_price + (half_spread * spread_adjustment)

    def generate_order_book(self, levels: int = 10) -> None:
        """Generate realistic order book with multiple price levels.

        Args:
            levels: Number of price levels on each side
        """
        self.bid_depth.clear()
        self.ask_depth.clear()

        # Generate bid side (buy orders)
        current_bid = self.bid
        for i in range(levels):
            price = current_bid - (self.spread * i)
            # Size increases with distance from mid (more liquidity deeper)
            size = random.randint(100, 500) * (i + 1)
            self.bid_depth.append((price, size))

        # Generate ask side (sell orders)
        current_ask = self.ask
        for i in range(levels):
            price = current_ask + (self.spread * i)
            size = random.randint(100, 500) * (i + 1)
            self.ask_depth.append((price, size))


class RealisticMarketSimulator:
    """Simulates realistic market behavior for testing."""

    def __init__(self) -> None:
        """Initialize the market simulator."""
        self.markets: Dict[str, MarketState] = {}
        self.time_elapsed: float = 0

        # Initialize default markets
        self._initialize_default_markets()

    def _initialize_default_markets(self) -> None:
        """Initialize common test symbols with realistic prices."""
        default_symbols = {
            "AAPL": (Decimal("150.00"), MarketCondition.NORMAL),
            "GOOGL": (Decimal("2800.00"), MarketCondition.VOLATILE),
            "MSFT": (Decimal("380.00"), MarketCondition.TRENDING_UP),
            "AMZN": (Decimal("3400.00"), MarketCondition.RANGE_BOUND),
            "TSLA": (Decimal("250.00"), MarketCondition.VOLATILE),
            "SPY": (Decimal("450.00"), MarketCondition.NORMAL),
        }

        for symbol, (price, condition) in default_symbols.items():
            spread = price * Decimal("0.0001")  # 1 basis point
            self.markets[symbol] = MarketState(
                symbol=symbol,
                last_price=price,
                bid=price - spread / 2,
                ask=price + spread / 2,
                spread=spread,
                condition=condition,
            )
            self.markets[symbol].generate_order_book()

    def add_symbol(self, symbol: str, initial_price: Decimal, condition: MarketCondition = MarketCondition.NORMAL) -> None:
        """Add a new symbol to the simulation.

        Args:
            symbol: Symbol to add
            initial_price: Starting price
            condition: Market condition for this symbol
        """
        spread = initial_price * Decimal("0.0001")
        self.markets[symbol] = MarketState(
            symbol=symbol,
            last_price=initial_price,
            bid=initial_price - spread / 2,
            ask=initial_price + spread / 2,
            spread=spread,
            condition=condition,
        )
        self.markets[symbol].generate_order_book()

    def update_all_markets(self, dt: float = 1.0) -> None:
        """Update all market prices.

        Args:
            dt: Time step in seconds
        """
        self.time_elapsed += dt

        for market in self.markets.values():
            market.update_price(dt)

            # Occasionally regenerate order book
            if random.random() < 0.1:  # 10% chance
                market.generate_order_book()

    def get_execution_price(
        self, symbol: str, side: common_pb2.OrderSide, quantity: Decimal, order_type: common_pb2.OrderType, limit_price: Optional[Decimal] = None
    ) -> Optional[Decimal]:
        """Get execution price for an order considering market impact.

        Args:
            symbol: Symbol to trade
            side: Buy or sell
            quantity: Order quantity
            order_type: Market or limit
            limit_price: Limit price for limit orders

        Returns:
            Execution price or None if order cannot be filled
        """
        if symbol not in self.markets:
            return None

        market = self.markets[symbol]

        # Market orders
        if order_type == common_pb2.ORDER_TYPE_MARKET:
            if side == common_pb2.ORDER_SIDE_BUY:
                # Buy at ask + slippage
                base_price = market.ask
                slippage = self._calculate_slippage(quantity, market.ask_depth)
            else:
                # Sell at bid - slippage
                base_price = market.bid
                slippage = -self._calculate_slippage(quantity, market.bid_depth)

            return base_price + slippage

        # Limit orders
        elif order_type == common_pb2.ORDER_TYPE_LIMIT:
            if limit_price is None:
                return None

            if side == common_pb2.ORDER_SIDE_BUY:
                # Buy limit - can only execute at limit or better (lower)
                if limit_price >= market.ask:
                    return market.ask  # Immediate execution
                else:
                    # Would go on book, simulate possible execution
                    if random.random() < 0.3:  # 30% fill probability
                        return limit_price
                    return None
            else:
                # Sell limit - can only execute at limit or better (higher)
                if limit_price <= market.bid:
                    return market.bid  # Immediate execution
                else:
                    if random.random() < 0.3:
                        return limit_price
                    return None

        return None

    def _calculate_slippage(self, quantity: Decimal, order_book: List[Tuple[Decimal, int]]) -> Decimal:
        """Calculate price impact based on order size and book depth.

        Args:
            quantity: Order quantity
            order_book: List of (price, size) tuples

        Returns:
            Price impact as decimal
        """
        remaining_qty = quantity
        weighted_price = Decimal("0")
        total_filled = Decimal("0")

        for _, (price, size) in enumerate(order_book):
            if remaining_qty <= 0:
                break

            fill_qty = min(remaining_qty, Decimal(str(size)))
            weighted_price += price * fill_qty
            total_filled += fill_qty
            remaining_qty -= fill_qty

        if total_filled > 0:
            avg_price = weighted_price / total_filled
            # Return difference from best price
            return abs(avg_price - order_book[0][0])

        # If we exhausted the book, add significant impact
        return order_book[0][0] * Decimal("0.01")  # 1% impact

    def simulate_partial_fill(self, quantity: Decimal) -> List[Decimal]:
        """Simulate partial fills for a large order.

        Args:
            quantity: Total order quantity

        Returns:
            List of fill quantities
        """
        fills = []
        remaining = quantity

        while remaining > 0:
            # Random fill size between 10% and 50% of remaining
            fill_pct = Decimal(str(random.uniform(0.1, 0.5)))
            fill_qty = min(remaining, remaining * fill_pct)

            # Round to reasonable lot size
            fill_qty = Decimal(str(int(fill_qty)))
            if fill_qty < 1:
                fill_qty = remaining

            fills.append(fill_qty)
            remaining -= fill_qty

        return fills

    def should_reject_order(self, symbol: str, order_type: common_pb2.OrderType, limit_price: Optional[Decimal] = None) -> Tuple[bool, str]:
        """Determine if an order should be rejected.

        Args:
            symbol: Symbol to trade
            order_type: Order type
            limit_price: Limit price for limit orders

        Returns:
            Tuple of (should_reject, reason)
        """
        if symbol not in self.markets:
            return True, "Symbol not found"

        market = self.markets[symbol]

        # Simulate occasional rejections
        if random.random() < 0.05:  # 5% random rejection
            reasons = [
                "Market closed",
                "Symbol halted",
                "Insufficient liquidity",
                "Risk check failed",
            ]
            return True, random.choice(reasons)

        # Check limit price reasonableness
        if order_type == common_pb2.ORDER_TYPE_LIMIT and limit_price:
            # Reject if limit price too far from market
            distance = abs(limit_price - market.last_price) / market.last_price
            if distance > Decimal("0.1"):  # 10% away
                return True, "Limit price too far from market"

        return False, ""
