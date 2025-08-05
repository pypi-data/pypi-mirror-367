"""Event models for strategy notifications.

This module contains models for various events that strategies receive,
including order updates, position changes, account updates, trades, and system events.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional, Union

from pydantic import BaseModel, Field, field_validator

from tektii.strategy.grpc import market_data_pb2, orders_pb2
from tektii.strategy.models.conversions import decimal_from_proto, decimal_from_proto_required, proto_from_decimal
from tektii.strategy.models.enums import OrderSide, OrderStatus, OrderType
from tektii.strategy.models.errors import SystemEventType
from tektii.strategy.models.market_data import BarData, OptionGreeks, TickData


class OrderUpdateEvent(BaseModel):
    """Notifies of order status changes.

    Sent whenever an order's status changes, including submissions,
    fills, cancellations, and rejections.
    """

    order_id: str = Field(..., description="Unique order identifier")
    symbol: str = Field(..., description="Trading symbol")
    status: OrderStatus = Field(..., description="Current order status")
    side: OrderSide = Field(..., description="Buy or sell side")
    order_type: OrderType = Field(..., description="Order type (market, limit, etc.)")

    # Quantities
    quantity: Decimal = Field(..., description="Original order quantity")
    filled_quantity: Decimal = Field(..., description="Quantity filled so far")
    remaining_quantity: Decimal = Field(..., description="Quantity remaining to fill")

    # Prices
    limit_price: Optional[Decimal] = Field(None, description="Limit price (for limit orders)")
    stop_price: Optional[Decimal] = Field(None, description="Stop price (for stop orders)")
    avg_fill_price: Optional[Decimal] = Field(None, description="Average fill price")

    # Timestamps
    created_at_us: int = Field(..., description="Order creation time (microseconds since epoch)")
    updated_at_us: int = Field(..., description="Last update time (microseconds since epoch)")

    # Additional information
    reject_reason: Optional[str] = Field(None, description="Rejection reason if rejected")
    metadata: Dict[str, str] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        """Pydantic model configuration."""

        frozen = True
        arbitrary_types_allowed = True

    @field_validator("quantity", "filled_quantity", "remaining_quantity", "limit_price", "stop_price", "avg_fill_price")
    @classmethod
    def validate_decimal(cls, v: Any) -> Optional[Decimal]:
        """Ensure all numeric fields are Decimal."""
        if v is None:
            return None
        if isinstance(v, (int, float, str)):
            return Decimal(str(v))
        if isinstance(v, Decimal):
            return v
        raise ValueError(f"Cannot convert {type(v)} to Decimal")

    @property
    def created_at(self) -> datetime:
        """Get creation time as datetime.

        Returns:
            Order creation timestamp
        """
        return datetime.fromtimestamp(self.created_at_us / 1_000_000)

    @property
    def updated_at(self) -> datetime:
        """Get update time as datetime.

        Returns:
            Last update timestamp
        """
        return datetime.fromtimestamp(self.updated_at_us / 1_000_000)

    @property
    def is_filled(self) -> bool:
        """Check if order is completely filled.

        Returns:
            True if order is fully filled
        """
        return self.status == OrderStatus.FILLED

    @property
    def is_active(self) -> bool:
        """Check if order is still active.

        Returns:
            True if order can still be filled or canceled
        """
        return self.status in [
            OrderStatus.PENDING,
            OrderStatus.SUBMITTED,
            OrderStatus.ACCEPTED,
            OrderStatus.PARTIAL,
        ]

    @property
    def is_terminal(self) -> bool:
        """Check if order is in terminal state.

        Returns:
            True if order is in final state
        """
        return self.status in [
            OrderStatus.FILLED,
            OrderStatus.CANCELED,
            OrderStatus.REJECTED,
            OrderStatus.EXPIRED,
        ]

    @property
    def fill_percentage(self) -> Decimal:
        """Percentage of order that has been filled.

        Returns:
            Percentage of order filled
        """
        if self.quantity == 0:
            return Decimal(0)
        return (self.filled_quantity / self.quantity) * 100

    def to_proto(self) -> market_data_pb2.OrderUpdateEvent:
        """Convert to proto message.

        Returns:
            Proto OrderUpdateEvent message
        """
        return market_data_pb2.OrderUpdateEvent(
            order_id=self.order_id,
            symbol=self.symbol,
            status=self.status.to_proto(),
            side=self.side.to_proto(),
            order_type=self.order_type.to_proto(),
            quantity=proto_from_decimal(self.quantity),
            filled_quantity=proto_from_decimal(self.filled_quantity),
            remaining_quantity=proto_from_decimal(self.remaining_quantity),
            limit_price=proto_from_decimal(self.limit_price),
            stop_price=proto_from_decimal(self.stop_price),
            avg_fill_price=proto_from_decimal(self.avg_fill_price),
            created_at_us=self.created_at_us,
            updated_at_us=self.updated_at_us,
            reject_reason=self.reject_reason or "",
            metadata=self.metadata,
        )

    @classmethod
    def from_proto(cls, proto: market_data_pb2.OrderUpdateEvent) -> OrderUpdateEvent:
        """Create from proto message.

        Args:
            proto: Proto OrderUpdateEvent message

        Returns:
            OrderUpdateEvent instance
        """
        return cls(
            order_id=proto.order_id,
            symbol=proto.symbol,
            status=OrderStatus.from_proto(proto.status),
            side=OrderSide.from_proto(proto.side),
            order_type=OrderType.from_proto(proto.order_type),
            quantity=decimal_from_proto_required(proto.quantity),
            filled_quantity=decimal_from_proto_required(proto.filled_quantity),
            remaining_quantity=decimal_from_proto_required(proto.remaining_quantity),
            limit_price=decimal_from_proto(proto.limit_price),
            stop_price=decimal_from_proto(proto.stop_price),
            avg_fill_price=decimal_from_proto(proto.avg_fill_price),
            created_at_us=proto.created_at_us,
            updated_at_us=proto.updated_at_us,
            reject_reason=proto.reject_reason if proto.reject_reason else None,
            metadata=dict(proto.metadata) if proto.metadata else {},
        )

    def __str__(self) -> str:
        """Human-readable string representation."""
        status_icon = "✓" if self.is_filled else "✗" if self.status == OrderStatus.REJECTED else "⋯"
        price_info = ""
        if self.order_type == OrderType.LIMIT:
            price_info = f" @ {self.limit_price:.2f}"
        elif self.avg_fill_price:
            price_info = f" @ {self.avg_fill_price:.2f} avg"

        return (
            f"{status_icon} Order {self.order_id}: {self.side.value} {self.quantity} {self.symbol}"
            f"{price_info} [{self.status.value}] ({self.fill_percentage:.0f}% filled)"
        )


class PositionUpdateEvent(BaseModel):
    """Notifies of position changes.

    Sent when a position's size, value, or P&L changes due to fills or market moves.
    """

    symbol: str = Field(..., description="Trading symbol")
    quantity: Decimal = Field(..., description="Current position size (positive=long, negative=short)")
    avg_price: Decimal = Field(..., description="Average entry price")

    # P&L information
    unrealized_pnl: Decimal = Field(..., description="Unrealized profit/loss")
    realized_pnl: Decimal = Field(..., description="Realized profit/loss")
    market_value: Decimal = Field(..., description="Current market value")

    # Current market prices
    current_price: Decimal = Field(..., description="Current market price")
    bid: Optional[Decimal] = Field(None, description="Current bid price")
    ask: Optional[Decimal] = Field(None, description="Current ask price")

    class Config:
        """Pydantic model configuration."""

        frozen = True
        arbitrary_types_allowed = True

    @field_validator("quantity", "avg_price", "unrealized_pnl", "realized_pnl", "market_value", "current_price", "bid", "ask")
    @classmethod
    def validate_decimal(cls, v: Any) -> Optional[Decimal]:
        """Ensure all numeric fields are Decimal."""
        if v is None:
            return None
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
    def is_flat(self) -> bool:
        """Check if position is flat (closed).

        Returns:
            True if position quantity is zero
        """
        return self.quantity == 0

    @property
    def total_pnl(self) -> Decimal:
        """Total P&L including realized and unrealized.

        Returns:
            Sum of realized and unrealized P&L
        """
        return self.realized_pnl + self.unrealized_pnl

    @property
    def return_percentage(self) -> Decimal:
        """Return percentage based on cost basis.

        Returns:
            Return as percentage of investment
        """
        if self.avg_price == 0:
            return Decimal(0)

        cost_basis = abs(self.quantity) * self.avg_price
        if cost_basis == 0:
            return Decimal(0)

        return (self.unrealized_pnl / cost_basis) * 100

    def to_proto(self) -> market_data_pb2.PositionUpdateEvent:
        """Convert to proto message.

        Returns:
            Proto PositionUpdateEvent message
        """
        return market_data_pb2.PositionUpdateEvent(
            symbol=self.symbol,
            quantity=proto_from_decimal(self.quantity),
            avg_price=proto_from_decimal(self.avg_price),
            unrealized_pnl=proto_from_decimal(self.unrealized_pnl),
            realized_pnl=proto_from_decimal(self.realized_pnl),
            market_value=proto_from_decimal(self.market_value),
            current_price=proto_from_decimal(self.current_price),
            bid=proto_from_decimal(self.bid),
            ask=proto_from_decimal(self.ask),
        )

    @classmethod
    def from_proto(cls, proto: market_data_pb2.PositionUpdateEvent) -> PositionUpdateEvent:
        """Create from proto message.

        Args:
            proto: Proto PositionUpdateEvent message

        Returns:
            PositionUpdateEvent instance
        """
        return cls(
            symbol=proto.symbol,
            quantity=decimal_from_proto_required(proto.quantity),
            avg_price=decimal_from_proto_required(proto.avg_price),
            unrealized_pnl=decimal_from_proto_required(proto.unrealized_pnl),
            realized_pnl=decimal_from_proto_required(proto.realized_pnl),
            market_value=decimal_from_proto_required(proto.market_value),
            current_price=decimal_from_proto_required(proto.current_price),
            bid=decimal_from_proto(proto.bid),
            ask=decimal_from_proto(proto.ask),
        )

    def __str__(self) -> str:
        """Human-readable string representation."""
        if self.is_flat:
            return f"Position {self.symbol}: FLAT (Realized P&L: {self.realized_pnl:+,.2f})"

        side = "Long" if self.is_long else "Short"
        return (
            f"Position {self.symbol}: {side} {abs(self.quantity)} @ {self.avg_price:.2f} "
            f"(Current: {self.current_price:.2f}, P&L: {self.total_pnl:+,.2f}, "
            f"{self.return_percentage:+.1f}%)"
        )


class AccountUpdateEvent(BaseModel):
    """Notifies of account balance changes.

    Sent when account balances, buying power, or margin requirements change.
    """

    # Balance information
    cash_balance: Decimal = Field(..., description="Available cash")
    portfolio_value: Decimal = Field(..., description="Total portfolio value")
    buying_power: Decimal = Field(..., description="Available buying power")

    # Margin information
    initial_margin: Decimal = Field(..., description="Initial margin requirement")
    maintenance_margin: Decimal = Field(..., description="Maintenance margin requirement")
    margin_used: Decimal = Field(..., description="Currently used margin")

    # P&L information
    daily_pnl: Decimal = Field(..., description="Today's P&L")
    total_pnl: Decimal = Field(..., description="Total P&L")

    # Risk metrics
    leverage: Optional[Decimal] = Field(None, description="Current leverage ratio")
    risk_metrics: Dict[str, Decimal] = Field(default_factory=dict, description="Additional risk metrics")

    class Config:
        """Pydantic model configuration."""

        frozen = True
        arbitrary_types_allowed = True

    @field_validator(
        "cash_balance", "portfolio_value", "buying_power", "initial_margin", "maintenance_margin", "margin_used", "daily_pnl", "total_pnl", "leverage"
    )
    @classmethod
    def validate_decimal(cls, v: Any) -> Optional[Decimal]:
        """Ensure all numeric fields are Decimal."""
        if v is None:
            return None
        if isinstance(v, (int, float, str)):
            return Decimal(str(v))
        if isinstance(v, Decimal):
            return v
        raise ValueError(f"Cannot convert {type(v)} to Decimal")

    @field_validator("risk_metrics")
    @classmethod
    def validate_risk_metrics(cls, v: Dict[str, Any]) -> Dict[str, Decimal]:
        """Ensure risk metrics values are Decimal."""
        result = {}
        for key, value in v.items():
            if isinstance(value, (int, float, str)):
                result[key] = Decimal(str(value))
            elif isinstance(value, Decimal):
                result[key] = value
            else:
                result[key] = Decimal(0)
        return result

    @property
    def margin_utilization(self) -> Decimal:
        """Margin utilization as a percentage.

        Returns:
            Margin used as percentage of initial margin
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
    def calculated_leverage(self) -> Decimal:
        """Leverage ratio calculated from portfolio and cash.

        Returns:
            Leverage ratio
        """
        if self.leverage is not None:
            return self.leverage
        if self.cash_balance == 0:
            return Decimal(0)
        return self.portfolio_value / self.cash_balance

    def to_proto(self) -> market_data_pb2.AccountUpdateEvent:
        """Convert to proto message.

        Returns:
            Proto AccountUpdateEvent message
        """
        risk_metrics_proto = {k: proto_from_decimal(v) for k, v in self.risk_metrics.items()}

        return market_data_pb2.AccountUpdateEvent(
            cash_balance=proto_from_decimal(self.cash_balance),
            portfolio_value=proto_from_decimal(self.portfolio_value),
            buying_power=proto_from_decimal(self.buying_power),
            initial_margin=proto_from_decimal(self.initial_margin),
            maintenance_margin=proto_from_decimal(self.maintenance_margin),
            margin_used=proto_from_decimal(self.margin_used),
            daily_pnl=proto_from_decimal(self.daily_pnl),
            total_pnl=proto_from_decimal(self.total_pnl),
            leverage=proto_from_decimal(self.leverage),
            risk_metrics=risk_metrics_proto,
        )

    @classmethod
    def from_proto(cls, proto: market_data_pb2.AccountUpdateEvent) -> AccountUpdateEvent:
        """Create from proto message.

        Args:
            proto: Proto AccountUpdateEvent message

        Returns:
            AccountUpdateEvent instance
        """
        risk_metrics = {k: decimal_from_proto_required(v) for k, v in proto.risk_metrics.items()}

        return cls(
            cash_balance=decimal_from_proto_required(proto.cash_balance),
            portfolio_value=decimal_from_proto_required(proto.portfolio_value),
            buying_power=decimal_from_proto_required(proto.buying_power),
            initial_margin=decimal_from_proto_required(proto.initial_margin),
            maintenance_margin=decimal_from_proto_required(proto.maintenance_margin),
            margin_used=decimal_from_proto_required(proto.margin_used),
            daily_pnl=decimal_from_proto_required(proto.daily_pnl),
            total_pnl=decimal_from_proto_required(proto.total_pnl),
            leverage=decimal_from_proto(proto.leverage),
            risk_metrics=risk_metrics,
        )

    def __str__(self) -> str:
        """Human-readable string representation."""
        return (
            f"Account: ${self.portfolio_value:,.2f} "
            f"(Cash: ${self.cash_balance:,.2f}, BP: ${self.buying_power:,.2f}, "
            f"Margin: {self.margin_utilization:.1f}%, P&L: ${self.total_pnl:+,.2f})"
        )


class TradeEvent(BaseModel):
    """Represents an individual trade execution.

    Sent when an order is filled (partially or completely), providing
    execution details including price, quantity, and fees.
    """

    trade_id: str = Field(..., description="Unique trade identifier")
    order_id: str = Field(..., description="Associated order ID")
    symbol: str = Field(..., description="Trading symbol")

    side: OrderSide = Field(..., description="Buy or sell side")
    quantity: Decimal = Field(..., description="Trade quantity")
    price: Decimal = Field(..., description="Execution price")

    timestamp_us: int = Field(..., description="Execution time (microseconds since epoch)")

    # Fees and commissions
    commission: Decimal = Field(Decimal(0), description="Commission charged")
    fees: Decimal = Field(Decimal(0), description="Other fees (SEC, TAF, etc.)")

    class Config:
        """Pydantic model configuration."""

        frozen = True
        arbitrary_types_allowed = True

    @field_validator("quantity", "price", "commission", "fees")
    @classmethod
    def validate_decimal(cls, v: Any) -> Decimal:
        """Ensure all numeric fields are Decimal."""
        if isinstance(v, (int, float, str)):
            return Decimal(str(v))
        if isinstance(v, Decimal):
            return v
        raise ValueError(f"Cannot convert {type(v)} to Decimal")

    @property
    def timestamp(self) -> datetime:
        """Get execution time as datetime.

        Returns:
            Trade execution timestamp
        """
        return datetime.fromtimestamp(self.timestamp_us / 1_000_000)

    @property
    def gross_value(self) -> Decimal:
        """Gross trade value before fees.

        Returns:
            Quantity * price
        """
        return self.quantity * self.price

    @property
    def total_cost(self) -> Decimal:
        """Total cost including all fees.

        Returns:
            Total cost (gross value + commission + fees for buys,
                      gross value - commission - fees for sells)
        """
        total_fees = self.commission + self.fees
        if self.side == OrderSide.BUY:
            return self.gross_value + total_fees
        else:
            return self.gross_value - total_fees

    @property
    def net_proceeds(self) -> Decimal:
        """Net proceeds after fees for sell orders.

        Returns:
            Net amount received after fees
        """
        if self.side == OrderSide.SELL:
            return self.gross_value - self.commission - self.fees
        return Decimal(0)

    def to_proto(self) -> market_data_pb2.TradeEvent:
        """Convert to proto message.

        Returns:
            Proto TradeEvent message
        """
        return market_data_pb2.TradeEvent(
            trade_id=self.trade_id,
            order_id=self.order_id,
            symbol=self.symbol,
            side=self.side.to_proto(),
            quantity=proto_from_decimal(self.quantity),
            price=proto_from_decimal(self.price),
            timestamp_us=self.timestamp_us,
            commission=proto_from_decimal(self.commission),
            fees=proto_from_decimal(self.fees),
        )

    @classmethod
    def from_proto(cls, proto: market_data_pb2.TradeEvent) -> TradeEvent:
        """Create from proto message.

        Args:
            proto: Proto TradeEvent message

        Returns:
            TradeEvent instance
        """
        return cls(
            trade_id=proto.trade_id,
            order_id=proto.order_id,
            symbol=proto.symbol,
            side=OrderSide.from_proto(proto.side),
            quantity=decimal_from_proto_required(proto.quantity),
            price=decimal_from_proto_required(proto.price),
            timestamp_us=proto.timestamp_us,
            commission=decimal_from_proto_required(proto.commission),
            fees=decimal_from_proto_required(proto.fees),
        )

    def __str__(self) -> str:
        """Human-readable string representation."""
        total_fees = self.commission + self.fees
        return (
            f"Trade {self.trade_id}: {self.side.value} {self.quantity} {self.symbol} "
            f"@ {self.price:.2f} (Value: ${self.gross_value:,.2f}, Fees: ${total_fees:.2f})"
        )


class SystemEvent(BaseModel):
    """Represents system-level notifications.

    Used for connection status, errors, warnings, and informational messages.
    """

    type: SystemEventType = Field(..., description="Type of system event")
    message: str = Field(..., description="Event message")
    details: Dict[str, str] = Field(default_factory=dict, description="Additional event details")

    class Config:
        """Pydantic model configuration."""

        frozen = True

    @property
    def is_error(self) -> bool:
        """Check if this is an error event.

        Returns:
            True if event type is ERROR
        """
        return self.type == SystemEventType.ERROR

    @property
    def is_warning(self) -> bool:
        """Check if this is a warning event.

        Returns:
            True if event type is WARNING
        """
        return self.type == SystemEventType.WARNING

    @property
    def is_connection_event(self) -> bool:
        """Check if this is a connection-related event.

        Returns:
            True if event is CONNECTED or DISCONNECTED
        """
        return self.type in [SystemEventType.CONNECTED, SystemEventType.DISCONNECTED]

    def to_proto(self) -> market_data_pb2.SystemEvent:
        """Convert to proto message.

        Returns:
            Proto SystemEvent message
        """
        return market_data_pb2.SystemEvent(
            type=self.type.to_proto(),
            message=self.message,
            details=self.details,
        )

    @classmethod
    def from_proto(cls, proto: market_data_pb2.SystemEvent) -> SystemEvent:
        """Create from proto message.

        Args:
            proto: Proto SystemEvent message

        Returns:
            SystemEvent instance
        """
        return cls(
            type=SystemEventType.from_proto(proto.type),
            message=proto.message,
            details=dict(proto.details) if proto.details else {},
        )

    def __str__(self) -> str:
        """Human-readable string representation."""
        icon_map = {
            SystemEventType.CONNECTED: "🟢",
            SystemEventType.DISCONNECTED: "🔴",
            SystemEventType.ERROR: "❌",
            SystemEventType.WARNING: "⚠️",
            SystemEventType.INFO: "ℹ️",
        }
        icon = icon_map.get(self.type, "•")

        details_str = ""
        if self.details:
            details_items = [f"{k}={v}" for k, v in self.details.items()]
            details_str = f" ({', '.join(details_items)})"

        return f"{icon} [{self.type.value}] {self.message}{details_str}"


class TektiiEvent(BaseModel):
    """Base event wrapper containing all possible event types.

    This is the main event model that strategies receive. It contains
    exactly one event payload along with metadata.
    """

    # Event metadata
    event_id: str = Field(..., description="Unique event identifier")
    timestamp_us: int = Field(..., description="Event timestamp (microseconds since epoch)")

    # Event payload - exactly one will be set
    tick_data: Optional[TickData] = Field(None, description="Tick data event")
    bar_data: Optional[BarData] = Field(None, description="Bar data event")
    option_greeks: Optional[OptionGreeks] = Field(None, description="Option Greeks event")
    order_update: Optional[OrderUpdateEvent] = Field(None, description="Order update event")
    position_update: Optional[PositionUpdateEvent] = Field(None, description="Position update event")
    account_update: Optional[AccountUpdateEvent] = Field(None, description="Account update event")
    trade: Optional[TradeEvent] = Field(None, description="Trade execution event")
    system: Optional[SystemEvent] = Field(None, description="System event")

    class Config:
        """Pydantic model configuration."""

        frozen = True
        arbitrary_types_allowed = True

    @property
    def timestamp(self) -> datetime:
        """Get event timestamp as datetime.

        Returns:
            Event timestamp
        """
        return datetime.fromtimestamp(self.timestamp_us / 1_000_000)

    @property
    def event_type(self) -> str:
        """Get the type of event contained.

        Returns:
            Name of the event type
        """
        if self.tick_data is not None:
            return "tick_data"
        elif self.bar_data is not None:
            return "bar_data"
        elif self.option_greeks is not None:
            return "option_greeks"
        elif self.order_update is not None:
            return "order_update"
        elif self.position_update is not None:
            return "position_update"
        elif self.account_update is not None:
            return "account_update"
        elif self.trade is not None:
            return "trade"
        elif self.system is not None:
            return "system"
        else:
            return "unknown"

    @property
    def event_payload(
        self,
    ) -> Union[TickData, BarData, OptionGreeks, OrderUpdateEvent, PositionUpdateEvent, AccountUpdateEvent, TradeEvent, SystemEvent, None]:
        """Get the actual event payload.

        Returns:
            The event data object
        """
        return (
            self.tick_data
            or self.bar_data
            or self.option_greeks
            or self.order_update
            or self.position_update
            or self.account_update
            or self.trade
            or self.system
        )

    def to_proto(self) -> orders_pb2.TektiiEvent:
        """Convert to proto message.

        Returns:
            Proto TektiiEvent message
        """
        proto = orders_pb2.TektiiEvent(
            event_id=self.event_id,
            timestamp_us=self.timestamp_us,
        )

        if self.tick_data is not None:
            proto.tick_data.CopyFrom(self.tick_data.to_proto())
        elif self.bar_data is not None:
            proto.bar_data.CopyFrom(self.bar_data.to_proto())
        elif self.option_greeks is not None:
            proto.option_greeks.CopyFrom(self.option_greeks.to_proto())
        elif self.order_update is not None:
            proto.order_update.CopyFrom(self.order_update.to_proto())
        elif self.position_update is not None:
            proto.position_update.CopyFrom(self.position_update.to_proto())
        elif self.account_update is not None:
            proto.account_update.CopyFrom(self.account_update.to_proto())
        elif self.trade is not None:
            proto.trade.CopyFrom(self.trade.to_proto())
        elif self.system is not None:
            proto.system.CopyFrom(self.system.to_proto())

        return proto

    @classmethod
    def from_proto(cls, proto: orders_pb2.TektiiEvent) -> TektiiEvent:
        """Create from proto message.

        Args:
            proto: Proto TektiiEvent message

        Returns:
            TektiiEvent instance
        """
        kwargs = {
            "event_id": proto.event_id,
            "timestamp_us": proto.timestamp_us,
        }

        # Check which event type is set
        which_one = proto.WhichOneof("event")
        if which_one == "tick_data":
            kwargs["tick_data"] = TickData.from_proto(proto.tick_data)
        elif which_one == "bar_data":
            kwargs["bar_data"] = BarData.from_proto(proto.bar_data)
        elif which_one == "option_greeks":
            kwargs["option_greeks"] = OptionGreeks.from_proto(proto.option_greeks)
        elif which_one == "order_update":
            kwargs["order_update"] = OrderUpdateEvent.from_proto(proto.order_update)
        elif which_one == "position_update":
            kwargs["position_update"] = PositionUpdateEvent.from_proto(proto.position_update)
        elif which_one == "account_update":
            kwargs["account_update"] = AccountUpdateEvent.from_proto(proto.account_update)
        elif which_one == "trade":
            kwargs["trade"] = TradeEvent.from_proto(proto.trade)
        elif which_one == "system":
            kwargs["system"] = SystemEvent.from_proto(proto.system)

        return cls(
            event_id=kwargs["event_id"],  # type: ignore[arg-type]
            timestamp_us=kwargs["timestamp_us"],  # type: ignore[arg-type]
            tick_data=kwargs.get("tick_data"),  # type: ignore[arg-type]
            bar_data=kwargs.get("bar_data"),  # type: ignore[arg-type]
            option_greeks=kwargs.get("option_greeks"),  # type: ignore[arg-type]
            order_update=kwargs.get("order_update"),  # type: ignore[arg-type]
            position_update=kwargs.get("position_update"),  # type: ignore[arg-type]
            account_update=kwargs.get("account_update"),  # type: ignore[arg-type]
            trade=kwargs.get("trade"),  # type: ignore[arg-type]
            system=kwargs.get("system"),  # type: ignore[arg-type]
        )

    def __str__(self) -> str:
        """Human-readable string representation."""
        timestamp_str = self.timestamp.strftime("%H:%M:%S.%f")[:-3]
        payload_str = str(self.event_payload) if self.event_payload else "Empty"
        return f"[{timestamp_str}] {self.event_type}: {payload_str}"
