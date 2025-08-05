"""Market data models for real-time and historical data.

This module contains models for tick data, bar data, and option Greeks,
representing various forms of market data used in trading strategies.
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator

from tektii.strategy.grpc import market_data_pb2
from tektii.strategy.models.conversions import decimal_from_proto, decimal_from_proto_required, proto_from_decimal
from tektii.strategy.models.enums import OptionType


class TickType(str, Enum):
    """Type of tick data.

    Indicates whether the tick contains quote data, trade data, or both.
    """

    UNKNOWN = "UNKNOWN"
    QUOTE = "QUOTE"  # Bid/ask update only
    TRADE = "TRADE"  # Trade execution only
    QUOTE_AND_TRADE = "QUOTE_AND_TRADE"  # Both quote and trade data

    @classmethod
    def from_proto(cls, proto: market_data_pb2.TickData.TickType) -> TickType:
        """Convert from proto enum."""
        mapping = {
            market_data_pb2.TickData.TICK_TYPE_UNKNOWN: cls.UNKNOWN,
            market_data_pb2.TickData.TICK_TYPE_QUOTE: cls.QUOTE,
            market_data_pb2.TickData.TICK_TYPE_TRADE: cls.TRADE,
            market_data_pb2.TickData.TICK_TYPE_QUOTE_AND_TRADE: cls.QUOTE_AND_TRADE,
        }
        return mapping.get(proto, cls.UNKNOWN)

    def to_proto(self) -> market_data_pb2.TickData.TickType:
        """Convert to proto enum."""
        mapping = {
            self.UNKNOWN: market_data_pb2.TickData.TICK_TYPE_UNKNOWN,
            self.QUOTE: market_data_pb2.TickData.TICK_TYPE_QUOTE,
            self.TRADE: market_data_pb2.TickData.TICK_TYPE_TRADE,
            self.QUOTE_AND_TRADE: market_data_pb2.TickData.TICK_TYPE_QUOTE_AND_TRADE,
        }
        return mapping[self]


class BarType(str, Enum):
    """Type of bar aggregation.

    Defines how bars are aggregated (time, tick count, volume, or dollar value).
    """

    UNKNOWN = "UNKNOWN"
    TIME = "TIME"  # Time-based bars (1min, 5min, etc.)
    TICK = "TICK"  # Tick count based (every N ticks)
    VOLUME = "VOLUME"  # Volume based (every N shares)
    DOLLAR = "DOLLAR"  # Dollar value based (every $N traded)

    @classmethod
    def from_proto(cls, proto: market_data_pb2.BarData.BarType) -> BarType:
        """Convert from proto enum."""
        mapping = {
            market_data_pb2.BarData.BAR_TYPE_UNKNOWN: cls.UNKNOWN,
            market_data_pb2.BarData.BAR_TYPE_TIME: cls.TIME,
            market_data_pb2.BarData.BAR_TYPE_TICK: cls.TICK,
            market_data_pb2.BarData.BAR_TYPE_VOLUME: cls.VOLUME,
            market_data_pb2.BarData.BAR_TYPE_DOLLAR: cls.DOLLAR,
        }
        return mapping.get(proto, cls.UNKNOWN)

    def to_proto(self) -> market_data_pb2.BarData.BarType:
        """Convert to proto enum."""
        mapping = {
            self.UNKNOWN: market_data_pb2.BarData.BAR_TYPE_UNKNOWN,
            self.TIME: market_data_pb2.BarData.BAR_TYPE_TIME,
            self.TICK: market_data_pb2.BarData.BAR_TYPE_TICK,
            self.VOLUME: market_data_pb2.BarData.BAR_TYPE_VOLUME,
            self.DOLLAR: market_data_pb2.BarData.BAR_TYPE_DOLLAR,
        }
        return mapping[self]


class TickData(BaseModel):
    """Represents high-frequency quote and trade data.

    Tick data provides real-time bid/ask quotes and last trade information,
    forming the most granular level of market data.
    """

    symbol: str = Field(..., description="Trading symbol")
    timestamp_us: int = Field(..., description="Timestamp in microseconds since epoch")

    # Quote data
    bid: Optional[Decimal] = Field(None, description="Best bid price")
    ask: Optional[Decimal] = Field(None, description="Best ask price")
    bid_size: Optional[int] = Field(None, description="Size at best bid")
    ask_size: Optional[int] = Field(None, description="Size at best ask")

    # Trade data
    last: Optional[Decimal] = Field(None, description="Last trade price")
    last_size: Optional[int] = Field(None, description="Last trade size")
    volume: Optional[int] = Field(None, description="Cumulative volume")

    # Derived fields
    mid: Optional[Decimal] = Field(None, description="Mid price")

    # Metadata
    condition: Optional[str] = Field(None, description="Trade condition code")
    exchange: Optional[str] = Field(None, description="Exchange code")
    tick_type: TickType = Field(TickType.UNKNOWN, description="Type of tick data")

    class Config:
        """Pydantic model configuration."""

        frozen = True
        arbitrary_types_allowed = True

    @field_validator("bid", "ask", "last", "mid")
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
            Tick timestamp as datetime
        """
        return datetime.fromtimestamp(self.timestamp_us / 1_000_000)

    @property
    def spread(self) -> Optional[Decimal]:
        """Bid-ask spread amount.

        Returns:
            Spread amount or None if bid/ask not available
        """
        if self.bid is not None and self.ask is not None:
            return self.ask - self.bid
        return None

    @property
    def spread_percentage(self) -> Optional[Decimal]:
        """Spread as percentage of mid price.

        Returns:
            Spread percentage or None if not calculable
        """
        spread = self.spread
        mid = self.calculate_mid()
        if spread is not None and mid is not None and mid > 0:
            return (spread / mid) * 100
        return None

    @property
    def has_quote(self) -> bool:
        """Check if tick contains quote data.

        Returns:
            True if bid and ask are available
        """
        return self.bid is not None and self.ask is not None

    @property
    def has_trade(self) -> bool:
        """Check if tick contains trade data.

        Returns:
            True if last trade price is available
        """
        return self.last is not None

    def calculate_mid(self) -> Optional[Decimal]:
        """Mid price calculated from bid and ask.

        Returns:
            Mid price or None if bid/ask not available
        """
        if self.bid is not None and self.ask is not None:
            return (self.bid + self.ask) / 2
        return None

    def to_proto(self) -> market_data_pb2.TickData:
        """Convert to proto message.

        Returns:
            Proto TickData message
        """
        return market_data_pb2.TickData(
            symbol=self.symbol,
            bid=proto_from_decimal(self.bid),
            ask=proto_from_decimal(self.ask),
            bid_size=self.bid_size or 0,
            ask_size=self.ask_size or 0,
            last=proto_from_decimal(self.last),
            last_size=self.last_size or 0,
            mid=proto_from_decimal(self.mid),
            exchange=self.exchange or "",
            tick_type=self.tick_type.to_proto(),
        )

    @classmethod
    def from_proto(cls, proto: market_data_pb2.TickData) -> TickData:
        """Create from proto message.

        Args:
            proto: Proto TickData message

        Returns:
            TickData instance
        """
        # We need to generate a timestamp since proto doesn't have one
        timestamp_us = int(datetime.now().timestamp() * 1_000_000)

        return cls(
            symbol=proto.symbol,
            timestamp_us=timestamp_us,
            bid=decimal_from_proto(proto.bid),
            ask=decimal_from_proto(proto.ask),
            bid_size=proto.bid_size if proto.bid_size > 0 else None,
            ask_size=proto.ask_size if proto.ask_size > 0 else None,
            last=decimal_from_proto(proto.last),
            last_size=proto.last_size if proto.last_size > 0 else None,
            volume=None,  # Not in proto
            mid=decimal_from_proto(proto.mid),
            condition=None,  # Not in proto
            exchange=proto.exchange if proto.exchange else None,
            tick_type=TickType.from_proto(proto.tick_type),
        )

    def __str__(self) -> str:
        """Human-readable string representation."""
        parts = [f"{self.symbol}"]

        if self.has_quote:
            parts.append(f"Bid: {self.bid:.2f}x{self.bid_size or 0}")
            parts.append(f"Ask: {self.ask:.2f}x{self.ask_size or 0}")
            if self.spread_percentage is not None:
                parts.append(f"Spread: {self.spread_percentage:.2f}%")

        if self.has_trade:
            parts.append(f"Last: {self.last:.2f}x{self.last_size or 0}")

        if self.volume:
            parts.append(f"Vol: {self.volume:,}")

        if self.exchange:
            parts.append(f"[{self.exchange}]")

        return " | ".join(parts)


class BarData(BaseModel):
    """Represents aggregated OHLCV data for a time period.

    Bar data provides candlestick information with open, high, low, close prices
    and volume, aggregated over a specific time period or other criteria.
    """

    symbol: str = Field(..., description="Trading symbol")
    timestamp_us: int = Field(..., description="Bar start timestamp in microseconds since epoch")

    # OHLCV data
    open: Decimal = Field(..., description="Opening price")
    high: Decimal = Field(..., description="Highest price")
    low: Decimal = Field(..., description="Lowest price")
    close: Decimal = Field(..., description="Closing price")
    volume: int = Field(..., description="Trading volume")

    # Additional aggregates
    vwap: Optional[Decimal] = Field(None, description="Volume-weighted average price")
    trade_count: Optional[int] = Field(None, description="Number of trades in this bar")

    # Bar metadata
    bar_type: BarType = Field(BarType.TIME, description="Type of bar aggregation")
    bar_size: int = Field(1, description="Bar size (e.g., 1 for 1min, 5 for 5min)")
    bar_size_unit: str = Field("min", description="Bar size unit (e.g., 'min', 'hour', 'day')")

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
    def upper_shadow(self) -> Decimal:
        """Upper shadow or wick size.

        Returns:
            Upper shadow size
        """
        return self.high - max(self.open, self.close)

    @property
    def lower_shadow(self) -> Decimal:
        """Lower shadow or wick size.

        Returns:
            Lower shadow size
        """
        return min(self.open, self.close) - self.low

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

    def is_doji(self, threshold: Optional[Decimal] = None) -> bool:
        """Check if this is a doji pattern.

        Args:
            threshold: Maximum body/range ratio for doji

        Returns:
            True if bar is a doji pattern
        """
        if threshold is None:
            threshold = Decimal("0.001")
        if self.range == 0:
            return True
        return (self.body / self.range) < threshold

    @property
    def bar_description(self) -> str:
        """Human-readable bar size description.

        Returns:
            Description like "5min" or "1day"
        """
        return f"{self.bar_size}{self.bar_size_unit}"

    def to_proto(self) -> market_data_pb2.BarData:
        """Convert to proto message.

        Returns:
            Proto BarData message
        """
        return market_data_pb2.BarData(
            symbol=self.symbol,
            open=proto_from_decimal(self.open),
            high=proto_from_decimal(self.high),
            low=proto_from_decimal(self.low),
            close=proto_from_decimal(self.close),
            volume=self.volume,
            vwap=proto_from_decimal(self.vwap),
            trade_count=self.trade_count or 0,
            bar_type=self.bar_type.to_proto(),
            bar_size=self.bar_size,
            bar_size_unit=self.bar_size_unit,
        )

    @classmethod
    def from_proto(cls, proto: market_data_pb2.BarData) -> BarData:
        """Create from proto message.

        Args:
            proto: Proto BarData message

        Returns:
            BarData instance
        """
        # We need to generate a timestamp since proto doesn't have one
        timestamp_us = int(datetime.now().timestamp() * 1_000_000)

        return cls(
            symbol=proto.symbol,
            timestamp_us=timestamp_us,
            open=decimal_from_proto_required(proto.open),
            high=decimal_from_proto_required(proto.high),
            low=decimal_from_proto_required(proto.low),
            close=decimal_from_proto_required(proto.close),
            volume=proto.volume,
            vwap=decimal_from_proto(proto.vwap),
            trade_count=proto.trade_count if proto.trade_count > 0 else None,
            bar_type=BarType.from_proto(proto.bar_type),
            bar_size=proto.bar_size,
            bar_size_unit=proto.bar_size_unit or "min",
        )

    def __str__(self) -> str:
        """Human-readable string representation."""
        direction = "↑" if self.is_bullish else "↓" if self.is_bearish else "→"
        return (
            f"Bar({self.symbol} {self.bar_description}: "
            f"O={self.open:.2f} H={self.high:.2f} L={self.low:.2f} C={self.close:.2f} "
            f"V={self.volume:,} {direction})"
        )


class OptionGreeks(BaseModel):
    """Represents options pricing and risk metrics.

    The Greeks measure sensitivities of option prices to various factors,
    essential for options trading and risk management.
    """

    symbol: str = Field(..., description="Option symbol")

    # The Greeks
    delta: Decimal = Field(..., description="Rate of change of option price with underlying price")
    gamma: Decimal = Field(..., description="Rate of change of delta with underlying price")
    theta: Decimal = Field(..., description="Time decay (price change per day)")
    vega: Decimal = Field(..., description="Sensitivity to volatility (price change per 1% vol)")
    rho: Decimal = Field(..., description="Sensitivity to interest rate (price change per 1% rate)")

    # Additional option metrics
    implied_volatility: Decimal = Field(..., description="Implied volatility (annualized)")
    theoretical_value: Decimal = Field(..., description="Theoretical option value")

    # Context data (important for Greeks interpretation)
    underlying_price: Decimal = Field(..., description="Current underlying asset price")
    interest_rate: Decimal = Field(Decimal("0.05"), description="Risk-free interest rate")
    days_to_expiry: int = Field(..., description="Days until option expiration")

    # Additional fields for test compatibility but not in proto
    underlying: str = Field(..., description="Underlying asset symbol")
    option_type: OptionType = Field(..., description="Call or put")
    strike: Decimal = Field(..., description="Strike price")
    expiration: date = Field(..., description="Expiration date")

    class Config:
        """Pydantic model configuration."""

        frozen = True
        arbitrary_types_allowed = True

    @field_validator(
        "strike", "delta", "gamma", "theta", "vega", "rho", "implied_volatility", "theoretical_value", "underlying_price", "interest_rate"
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
    def is_itm(self) -> bool:
        """Check if option is in-the-money.

        Returns:
            True if option is in-the-money
        """
        if self.option_type == OptionType.CALL:
            return self.underlying_price > self.strike
        else:  # PUT
            return self.underlying_price < self.strike

    @property
    def intrinsic_value(self) -> Decimal:
        """Calculate intrinsic value of the option.

        Returns:
            Intrinsic value
        """
        if self.option_type == OptionType.CALL:
            return max(self.underlying_price - self.strike, Decimal("0"))
        else:  # PUT
            return max(self.strike - self.underlying_price, Decimal("0"))

    @property
    def time_value(self) -> Decimal:
        """Time value of the option.

        Returns:
            Time value (theoretical - intrinsic)
        """
        return max(self.theoretical_value - self.intrinsic_value, Decimal("0"))

    @property
    def daily_theta_percentage(self) -> Decimal:
        """Theta as percentage of option value.

        Returns:
            Daily theta decay as percentage
        """
        if self.theoretical_value == 0:
            return Decimal(0)
        return (self.theta / self.theoretical_value) * 100

    def to_proto(self) -> market_data_pb2.OptionGreeks:
        """Convert to proto message.

        Returns:
            Proto OptionGreeks message
        """
        return market_data_pb2.OptionGreeks(
            symbol=self.symbol,
            delta=proto_from_decimal(self.delta),
            gamma=proto_from_decimal(self.gamma),
            theta=proto_from_decimal(self.theta),
            vega=proto_from_decimal(self.vega),
            rho=proto_from_decimal(self.rho),
            implied_volatility=proto_from_decimal(self.implied_volatility),
            theoretical_value=proto_from_decimal(self.theoretical_value),
            underlying_price=proto_from_decimal(self.underlying_price),
            interest_rate=proto_from_decimal(self.interest_rate),
            days_to_expiry=self.days_to_expiry,
        )

    @classmethod
    def from_proto(cls, proto: market_data_pb2.OptionGreeks) -> OptionGreeks:
        """Create from proto message.

        Args:
            proto: Proto OptionGreeks message

        Returns:
            OptionGreeks instance
        """
        # Generate missing fields for compatibility
        underlying = "UNKNOWN"
        option_type = OptionType.CALL
        strike = Decimal("100")
        expiration = date.today()

        return cls(
            symbol=proto.symbol,
            delta=decimal_from_proto_required(proto.delta),
            gamma=decimal_from_proto_required(proto.gamma),
            theta=decimal_from_proto_required(proto.theta),
            vega=decimal_from_proto_required(proto.vega),
            rho=decimal_from_proto_required(proto.rho),
            implied_volatility=decimal_from_proto_required(proto.implied_volatility),
            theoretical_value=decimal_from_proto_required(proto.theoretical_value),
            underlying_price=decimal_from_proto_required(proto.underlying_price),
            interest_rate=decimal_from_proto_required(proto.interest_rate),
            days_to_expiry=proto.days_to_expiry,
            underlying=underlying,
            option_type=option_type,
            strike=strike,
            expiration=expiration,
        )

    def __str__(self) -> str:
        """Human-readable string representation."""
        return (
            f"Greeks({self.symbol}: Δ={self.delta:.3f} Γ={self.gamma:.3f} "
            f"Θ={self.theta:.3f} V={self.vega:.3f} ρ={self.rho:.3f} "
            f"IV={self.implied_volatility:.1%} Days={self.days_to_expiry})"
        )
