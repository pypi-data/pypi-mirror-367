"""Common trading models used across the SDK.

This module contains core data structures like Position, AccountState, Bar,
and PriceLevel that are fundamental to trading operations.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator

from tektii.strategy.grpc import common_pb2
from tektii.strategy.models.conversions import decimal_from_proto, decimal_from_proto_required, proto_from_decimal


class Position(BaseModel):
    """Represents a current position in a trading account.

    A position tracks the quantity and value of securities held,
    along with profit/loss information.
    """

    symbol: str = Field(..., description="Trading symbol")
    quantity: Decimal = Field(..., description="Position size (positive=long, negative=short)")
    avg_price: Decimal = Field(..., description="Average entry price")
    market_value: Decimal = Field(..., description="Current market value of position")
    unrealized_pnl: Decimal = Field(..., description="Unrealized profit/loss")
    realized_pnl: Decimal = Field(..., description="Realized profit/loss")
    current_price: Decimal = Field(..., description="Current market price")

    class Config:
        """Pydantic model configuration."""

        frozen = True
        arbitrary_types_allowed = True

    @field_validator("quantity", "avg_price", "market_value", "unrealized_pnl", "realized_pnl", "current_price")
    @classmethod
    def validate_decimal(cls, v: Any) -> Decimal:
        """Ensure all numeric fields are Decimal."""
        if isinstance(v, (int, float, str)):
            return Decimal(str(v))
        if isinstance(v, Decimal):
            return v
        raise ValueError(f"Cannot convert {type(v)} to Decimal")

    @property
    def is_long(self) -> bool:
        """Check if this is a long position.

        Returns:
            True if position quantity is positive
        """
        return self.quantity > 0

    @property
    def is_short(self) -> bool:
        """Check if this is a short position.

        Returns:
            True if position quantity is negative
        """
        return self.quantity < 0

    @property
    def total_pnl(self) -> Decimal:
        """Total profit and loss for this position.

        Returns:
            Total profit/loss
        """
        return self.realized_pnl + self.unrealized_pnl

    @property
    def return_percentage(self) -> Decimal:
        """Return percentage based on the cost basis.

        Returns:
            Return as percentage of investment
        """
        if self.avg_price == 0:
            return Decimal(0)

        cost_basis = abs(self.quantity) * self.avg_price
        if cost_basis == 0:
            return Decimal(0)

        return (self.total_pnl / cost_basis) * 100

    def to_proto(self) -> common_pb2.Position:
        """Convert to proto message.

        Returns:
            Proto Position message
        """
        return common_pb2.Position(
            symbol=self.symbol,
            quantity=proto_from_decimal(self.quantity),
            avg_price=proto_from_decimal(self.avg_price),
            market_value=proto_from_decimal(self.market_value),
            unrealized_pnl=proto_from_decimal(self.unrealized_pnl),
            realized_pnl=proto_from_decimal(self.realized_pnl),
            current_price=proto_from_decimal(self.current_price),
        )

    @classmethod
    def from_proto(cls, proto: common_pb2.Position) -> Position:
        """Create from proto message.

        Args:
            proto: Proto Position message

        Returns:
            Position instance
        """
        return cls(
            symbol=proto.symbol,
            quantity=decimal_from_proto_required(proto.quantity),
            avg_price=decimal_from_proto_required(proto.avg_price),
            market_value=decimal_from_proto_required(proto.market_value),
            unrealized_pnl=decimal_from_proto_required(proto.unrealized_pnl),
            realized_pnl=decimal_from_proto_required(proto.realized_pnl),
            current_price=decimal_from_proto_required(proto.current_price),
        )

    def __str__(self) -> str:
        """Human-readable string representation."""
        side = "Long" if self.is_long else "Short"
        return f"{side} {abs(self.quantity)} {self.symbol} @ {self.avg_price:.2f} " f"(P&L: {self.total_pnl:+.2f}, {self.return_percentage:+.2f}%)"


class AccountState(BaseModel):
    """Represents the current state of a trading account.

    Tracks cash balances, margin requirements, and overall portfolio metrics.
    """

    cash_balance: Decimal = Field(..., description="Available cash")
    portfolio_value: Decimal = Field(..., description="Total portfolio value")
    buying_power: Decimal = Field(..., description="Available buying power")
    initial_margin: Decimal = Field(..., description="Initial margin requirement")
    maintenance_margin: Decimal = Field(..., description="Maintenance margin requirement")
    margin_used: Decimal = Field(..., description="Currently used margin")
    daily_pnl: Decimal = Field(..., description="Today's P&L")
    total_pnl: Decimal = Field(..., description="Total P&L")

    class Config:
        """Pydantic model configuration."""

        frozen = True
        arbitrary_types_allowed = True

    @field_validator(
        "cash_balance", "portfolio_value", "buying_power", "initial_margin", "maintenance_margin", "margin_used", "daily_pnl", "total_pnl"
    )
    @classmethod
    def validate_decimal(cls, v: Any) -> Decimal:
        """Ensure all numeric fields are Decimal."""
        if isinstance(v, (int, float, str)):
            return Decimal(str(v))
        if isinstance(v, Decimal):
            return v
        raise ValueError(f"Cannot convert {type(v)} to Decimal")

    @property
    def margin_utilization(self) -> Decimal:
        """Margin utilization as a percentage.

        Returns:
            Margin used as percentage of available margin
        """
        if self.initial_margin == 0:
            return Decimal(0)
        return (self.margin_used / self.initial_margin) * 100

    @property
    def excess_margin(self) -> Decimal:
        """Excess margin above maintenance requirements.

        Returns:
            Excess margin amount
        """
        return self.portfolio_value - self.maintenance_margin

    @property
    def leverage(self) -> Decimal:
        """Current leverage ratio.

        Returns:
            Leverage ratio
        """
        if self.cash_balance == 0:
            return Decimal(0)
        return self.portfolio_value / self.cash_balance

    def to_proto(self) -> common_pb2.AccountState:
        """Convert to proto message.

        Returns:
            Proto AccountState message
        """
        return common_pb2.AccountState(
            cash_balance=proto_from_decimal(self.cash_balance),
            portfolio_value=proto_from_decimal(self.portfolio_value),
            buying_power=proto_from_decimal(self.buying_power),
            initial_margin=proto_from_decimal(self.initial_margin),
            maintenance_margin=proto_from_decimal(self.maintenance_margin),
            margin_used=proto_from_decimal(self.margin_used),
            daily_pnl=proto_from_decimal(self.daily_pnl),
            total_pnl=proto_from_decimal(self.total_pnl),
        )

    @classmethod
    def from_proto(cls, proto: common_pb2.AccountState) -> AccountState:
        """Create from proto message.

        Args:
            proto: Proto AccountState message

        Returns:
            AccountState instance
        """
        return cls(
            cash_balance=decimal_from_proto_required(proto.cash_balance),
            portfolio_value=decimal_from_proto_required(proto.portfolio_value),
            buying_power=decimal_from_proto_required(proto.buying_power),
            initial_margin=decimal_from_proto_required(proto.initial_margin),
            maintenance_margin=decimal_from_proto_required(proto.maintenance_margin),
            margin_used=decimal_from_proto_required(proto.margin_used),
            daily_pnl=decimal_from_proto_required(proto.daily_pnl),
            total_pnl=decimal_from_proto_required(proto.total_pnl),
        )

    def __str__(self) -> str:
        """Human-readable string representation."""
        return (
            f"Account: ${self.portfolio_value:,.2f} "
            f"(Cash: ${self.cash_balance:,.2f}, "
            f"BP: ${self.buying_power:,.2f}, "
            f"P&L: ${self.total_pnl:+,.2f})"
        )


class Bar(BaseModel):
    """Represents OHLCV data for a time period.

    Standard candlestick/bar data with open, high, low, close, volume.
    """

    timestamp_us: int = Field(..., description="Start of bar period (microseconds since epoch)")
    open: Decimal = Field(..., description="Opening price")
    high: Decimal = Field(..., description="Highest price")
    low: Decimal = Field(..., description="Lowest price")
    close: Decimal = Field(..., description="Closing price")
    volume: int = Field(..., description="Trading volume")
    vwap: Optional[Decimal] = Field(None, description="Volume-weighted average price")

    class Config:
        """Pydantic model configuration."""

        frozen = True
        arbitrary_types_allowed = True

    @field_validator("open", "high", "low", "close", "vwap")
    @classmethod
    def validate_decimal(cls, v: Any) -> Optional[Decimal]:
        """Ensure all price fields are Decimal."""
        if v is None:
            return None
        if isinstance(v, (int, float, str)):
            return Decimal(str(v))
        if isinstance(v, Decimal):
            return v
        raise ValueError(f"Cannot convert {type(v)} to Decimal")

    @property
    def timestamp(self) -> datetime:
        """Get timestamp as datetime.

        Returns:
            Bar timestamp as datetime
        """
        return datetime.fromtimestamp(self.timestamp_us / 1_000_000)

    @property
    def range(self) -> Decimal:
        """Price range from high to low.

        Returns:
            Price range
        """
        return self.high - self.low

    @property
    def body(self) -> Decimal:
        """Candle body size as absolute difference.

        Returns:
            Absolute body size
        """
        return abs(self.close - self.open)

    @property
    def is_bullish(self) -> bool:
        """Check if this is a bullish bar.

        Returns:
            True if close > open
        """
        return self.close > self.open

    @property
    def is_bearish(self) -> bool:
        """Check if this is a bearish bar.

        Returns:
            True if close < open
        """
        return self.close < self.open

    def to_proto(self) -> common_pb2.Bar:
        """Convert to proto message.

        Returns:
            Proto Bar message
        """
        return common_pb2.Bar(
            timestamp_us=self.timestamp_us,
            open=proto_from_decimal(self.open),
            high=proto_from_decimal(self.high),
            low=proto_from_decimal(self.low),
            close=proto_from_decimal(self.close),
            volume=self.volume,
            vwap=proto_from_decimal(self.vwap) if self.vwap is not None else 0.0,
        )

    @classmethod
    def from_proto(cls, proto: common_pb2.Bar) -> Bar:
        """Create from proto message.

        Args:
            proto: Proto Bar message

        Returns:
            Bar instance
        """
        vwap = decimal_from_proto(proto.vwap) if proto.vwap > 0 else None
        return cls(
            timestamp_us=proto.timestamp_us,
            open=decimal_from_proto_required(proto.open),
            high=decimal_from_proto_required(proto.high),
            low=decimal_from_proto_required(proto.low),
            close=decimal_from_proto_required(proto.close),
            volume=proto.volume,
            vwap=vwap,
        )

    def __str__(self) -> str:
        """Human-readable string representation."""
        return (
            f"Bar({self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}: "
            f"O={self.open:.2f} H={self.high:.2f} L={self.low:.2f} C={self.close:.2f} V={self.volume:,})"
        )


class PriceLevel(BaseModel):
    """Represents a level in the order book.

    Used for market depth/Level 2 data.
    """

    price: Decimal = Field(..., description="Price level")
    size: Decimal = Field(..., description="Total size at this level")
    order_count: Optional[int] = Field(None, description="Number of orders at this level")

    class Config:
        """Pydantic model configuration."""

        frozen = True
        arbitrary_types_allowed = True

    @field_validator("price", "size")
    @classmethod
    def validate_decimal(cls, v: Any) -> Decimal:
        """Ensure all numeric fields are Decimal."""
        if isinstance(v, (int, float, str)):
            return Decimal(str(v))
        if isinstance(v, Decimal):
            return v
        raise ValueError(f"Cannot convert {type(v)} to Decimal")

    @property
    def notional_value(self) -> Decimal:
        """Notional value at this price level.

        Returns:
            Price * size
        """
        return self.price * self.size

    def to_proto(self) -> common_pb2.PriceLevel:
        """Convert to proto message.

        Returns:
            Proto PriceLevel message
        """
        return common_pb2.PriceLevel(
            price=proto_from_decimal(self.price),
            size=proto_from_decimal(self.size),
            order_count=self.order_count or 0,
        )

    @classmethod
    def from_proto(cls, proto: common_pb2.PriceLevel) -> PriceLevel:
        """Create from proto message.

        Args:
            proto: Proto PriceLevel message

        Returns:
            PriceLevel instance
        """
        return cls(
            price=decimal_from_proto_required(proto.price),
            size=decimal_from_proto_required(proto.size),
            order_count=proto.order_count if proto.order_count > 0 else None,
        )

    def __str__(self) -> str:
        """Human-readable string representation."""
        orders = f" ({self.order_count} orders)" if self.order_count else ""
        return f"{self.size:,.0f} @ {self.price:.2f}{orders}"
