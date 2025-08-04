"""Order-related models and builders.

This module contains models for orders, protective orders, and order builders
that provide a fluent API for constructing complex order requests.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional, Union

from pydantic import BaseModel, Field, field_validator, model_validator

from tektii.strategy.grpc import common_pb2, orders_pb2
from tektii.strategy.models.conversions import decimal_from_proto, decimal_from_proto_required, proto_from_decimal
from tektii.strategy.models.enums import OrderIntent, OrderSide, OrderStatus, OrderType, TimeInForce


class Order(BaseModel):
    """Represents a trading order.

    Comprehensive order information including status, fills, and metadata.
    """

    order_id: str = Field(..., description="Unique order identifier")
    symbol: str = Field(..., description="Trading symbol")
    status: OrderStatus = Field(..., description="Current order status")
    side: OrderSide = Field(..., description="Buy or sell")
    order_type: OrderType = Field(..., description="Order execution type")
    quantity: Decimal = Field(..., description="Total order quantity")
    filled_quantity: Decimal = Field(Decimal("0"), description="Quantity filled so far")
    limit_price: Optional[Decimal] = Field(None, description="Limit price (if applicable)")
    stop_price: Optional[Decimal] = Field(None, description="Stop price (if applicable)")
    created_at_us: int = Field(..., description="Creation timestamp (microseconds)")
    order_intent: OrderIntent = Field(OrderIntent.UNKNOWN, description="Order purpose")
    parent_trade_id: Optional[str] = Field(None, description="Parent trade ID for protective orders")

    class Config:
        """Pydantic model configuration."""

        frozen = True
        arbitrary_types_allowed = True

    @field_validator("quantity", "filled_quantity", "limit_price", "stop_price")
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

    @field_validator("status", mode="before")
    @classmethod
    def convert_status(cls, v: Any) -> OrderStatus:
        """Convert status value to OrderStatus."""
        if isinstance(v, OrderStatus):
            return v
        elif isinstance(v, int):
            return OrderStatus.from_proto(v)
        elif isinstance(v, str):
            return OrderStatus.from_string(v)
        else:
            raise ValueError(f"Invalid order status: {v}")

    @field_validator("side", mode="before")
    @classmethod
    def convert_side(cls, v: Any) -> OrderSide:
        """Convert side value to OrderSide."""
        if isinstance(v, OrderSide):
            return v
        elif isinstance(v, int):
            return OrderSide.from_proto(v)
        elif isinstance(v, str):
            return OrderSide.from_string(v)
        else:
            raise ValueError(f"Invalid order side: {v}")

    @field_validator("order_type", mode="before")
    @classmethod
    def convert_order_type(cls, v: Any) -> OrderType:
        """Convert order type value to OrderType."""
        if isinstance(v, OrderType):
            return v
        elif isinstance(v, int):
            return OrderType.from_proto(v)
        elif isinstance(v, str):
            return OrderType.from_string(v)
        else:
            raise ValueError(f"Invalid order type: {v}")

    @field_validator("order_intent", mode="before")
    @classmethod
    def convert_order_intent(cls, v: Any) -> OrderIntent:
        """Convert order intent value to OrderIntent."""
        if isinstance(v, OrderIntent):
            return v
        elif isinstance(v, int):
            return OrderIntent.from_proto(v)
        elif isinstance(v, str):
            return OrderIntent.from_string(v)
        else:
            raise ValueError(f"Invalid order intent: {v}")

    @model_validator(mode="after")
    def validate_prices(self) -> Order:
        """Validate price requirements based on order type."""
        if self.order_type.requires_limit_price() and self.limit_price is None:
            raise ValueError(f"{self.order_type} requires limit_price")
        if self.order_type.requires_stop_price() and self.stop_price is None:
            raise ValueError(f"{self.order_type} requires stop_price")
        return self

    @property
    def created_at(self) -> datetime:
        """Get creation time as datetime.

        Returns:
            Order creation timestamp
        """
        return datetime.fromtimestamp(self.created_at_us / 1_000_000)

    @property
    def remaining_quantity(self) -> Decimal:
        """Calculate remaining quantity to fill.

        Returns:
            Unfilled quantity
        """
        return self.quantity - self.filled_quantity

    @property
    def fill_percentage(self) -> Decimal:
        """Calculate fill percentage.

        Returns:
            Percentage of order filled
        """
        if self.quantity == 0:
            return Decimal(0)
        return (self.filled_quantity / self.quantity) * 100

    @property
    def is_filled(self) -> bool:
        """Check if order is completely filled.

        Returns:
            True if fully filled
        """
        return self.status == OrderStatus.FILLED

    @property
    def is_partially_filled(self) -> bool:
        """Check if order is partially filled.

        Returns:
            True if some quantity is filled but not all
        """
        return self.filled_quantity > 0 and self.filled_quantity < self.quantity

    @property
    def is_active(self) -> bool:
        """Check if order is still active.

        Returns:
            True if order can still be executed
        """
        return self.status.is_active()

    @property
    def is_terminal(self) -> bool:
        """Check if order is in terminal state.

        Returns:
            True if order is done (filled, canceled, rejected, or expired)
        """
        return self.status.is_terminal()

    def calculate_value(self) -> Optional[Decimal]:
        """Calculate the total order value.

        Returns:
            Order value based on quantity and price, or None for market orders
        """
        if self.order_type == OrderType.MARKET:
            return None
        elif self.order_type == OrderType.LIMIT and self.limit_price:
            return self.quantity * self.limit_price
        elif self.order_type == OrderType.STOP and self.stop_price:
            return self.quantity * self.stop_price
        elif self.order_type == OrderType.STOP_LIMIT and self.limit_price:
            return self.quantity * self.limit_price
        return None

    def to_proto(self) -> common_pb2.Order:
        """Convert to proto message.

        Returns:
            Proto Order message
        """
        return common_pb2.Order(
            order_id=self.order_id,
            symbol=self.symbol,
            status=self.status.value,  # Use int value for proto
            side=self.side.value,  # Use int value for proto
            order_type=self.order_type.value,  # Use int value for proto
            quantity=proto_from_decimal(self.quantity),
            filled_quantity=proto_from_decimal(self.filled_quantity),
            limit_price=proto_from_decimal(self.limit_price) if self.limit_price else 0.0,
            stop_price=proto_from_decimal(self.stop_price) if self.stop_price else 0.0,
            created_at_us=self.created_at_us,
            order_intent=self.order_intent.value,  # Use int value for proto
            parent_trade_id=self.parent_trade_id or "",
        )

    @classmethod
    def from_proto(cls, proto: common_pb2.Order) -> Order:
        """Create from proto message.

        Args:
            proto: Proto Order message

        Returns:
            Order instance
        """
        return cls(
            order_id=proto.order_id,
            symbol=proto.symbol,
            status=int(proto.status),  # type: ignore[arg-type]  # Field validator converts
            side=int(proto.side),  # type: ignore[arg-type]  # Field validator converts
            order_type=int(proto.order_type),  # type: ignore[arg-type]  # Field validator converts
            quantity=decimal_from_proto_required(proto.quantity),
            filled_quantity=decimal_from_proto_required(proto.filled_quantity),
            limit_price=decimal_from_proto(proto.limit_price) if proto.limit_price > 0 else None,
            stop_price=decimal_from_proto(proto.stop_price) if proto.stop_price > 0 else None,
            created_at_us=proto.created_at_us,
            order_intent=int(proto.order_intent),  # type: ignore[arg-type]  # Field validator converts
            parent_trade_id=proto.parent_trade_id if proto.parent_trade_id else None,
        )

    def __str__(self) -> str:
        """Human-readable string representation."""
        price_info = ""
        if self.limit_price:
            price_info = f" @ {self.limit_price:.2f}"
        if self.stop_price:
            price_info += f" stop={self.stop_price:.2f}"

        fill_info = ""
        if self.is_partially_filled:
            fill_info = f" ({self.filled_quantity}/{self.quantity} filled)"

        return f"{self.status} {self.order_type} {self.side} " f"{self.quantity} {self.symbol}{price_info}{fill_info}"


class StopOrder(BaseModel):
    """Configuration for stop market orders."""

    stop_price: Decimal = Field(..., description="Stop trigger price")

    class Config:
        """Pydantic model configuration."""

        frozen = True
        arbitrary_types_allowed = True

    @field_validator("stop_price")
    @classmethod
    def validate_decimal(cls, v: Any) -> Decimal:
        """Ensure stop price is Decimal."""
        if isinstance(v, (int, float, str)):
            return Decimal(str(v))
        if isinstance(v, Decimal):
            return v
        raise ValueError(f"Cannot convert {type(v)} to Decimal")

    def to_proto(self) -> common_pb2.StopOrder:
        """Convert to proto message."""
        return common_pb2.StopOrder(stop_price=proto_from_decimal(self.stop_price))

    @classmethod
    def from_proto(cls, proto: common_pb2.StopOrder) -> StopOrder:
        """Create from proto message."""
        return cls(stop_price=decimal_from_proto_required(proto.stop_price))


class StopLimitOrder(BaseModel):
    """Configuration for stop limit orders."""

    stop_price: Decimal = Field(..., description="Stop trigger price")
    limit_price: Decimal = Field(..., description="Limit price after stop triggers")

    class Config:
        """Pydantic model configuration."""

        frozen = True
        arbitrary_types_allowed = True

    @field_validator("stop_price", "limit_price")
    @classmethod
    def validate_decimal(cls, v: Any) -> Decimal:
        """Ensure prices are Decimal."""
        if isinstance(v, (int, float, str)):
            return Decimal(str(v))
        if isinstance(v, Decimal):
            return v
        raise ValueError(f"Cannot convert {type(v)} to Decimal")

    def to_proto(self) -> common_pb2.StopLimitOrder:
        """Convert to proto message."""
        return common_pb2.StopLimitOrder(
            stop_price=proto_from_decimal(self.stop_price),
            limit_price=proto_from_decimal(self.limit_price),
        )

    @classmethod
    def from_proto(cls, proto: common_pb2.StopLimitOrder) -> StopLimitOrder:
        """Create from proto message."""
        return cls(
            stop_price=decimal_from_proto_required(proto.stop_price),
            limit_price=decimal_from_proto_required(proto.limit_price),
        )


class ProtectiveOrdersOnFill(BaseModel):
    """Defines protective orders to create when an order fills.

    Used to automatically create stop loss and take profit orders.
    """

    stop_loss: Optional[Union[StopOrder, StopLimitOrder]] = Field(default=None, description="Stop loss configuration")
    take_profit_price: Optional[Decimal] = Field(default=None, description="Take profit limit price")

    class Config:
        """Pydantic model configuration."""

        frozen = True
        arbitrary_types_allowed = True

    @field_validator("take_profit_price")
    @classmethod
    def validate_decimal(cls, v: Any) -> Optional[Decimal]:
        """Ensure take profit price is Decimal."""
        if v is None:
            return None
        if isinstance(v, (int, float, str)):
            return Decimal(str(v))
        if isinstance(v, Decimal):
            return v
        raise ValueError(f"Cannot convert {type(v)} to Decimal")

    def to_proto(self) -> common_pb2.ProtectiveOrdersOnFill:
        """Convert to proto message."""
        proto = common_pb2.ProtectiveOrdersOnFill()

        if self.stop_loss:
            if isinstance(self.stop_loss, StopOrder):
                proto.stop.CopyFrom(self.stop_loss.to_proto())
            elif isinstance(self.stop_loss, StopLimitOrder):
                proto.stop_limit.CopyFrom(self.stop_loss.to_proto())

        if self.take_profit_price:
            proto.take_profit_price = proto_from_decimal(self.take_profit_price)

        return proto

    @classmethod
    def from_proto(cls, proto: common_pb2.ProtectiveOrdersOnFill) -> ProtectiveOrdersOnFill:
        """Create from proto message."""
        stop_loss: Optional[Union[StopOrder, StopLimitOrder]] = None
        if proto.HasField("stop"):
            stop_loss = StopOrder.from_proto(proto.stop)
        elif proto.HasField("stop_limit"):
            stop_loss = StopLimitOrder.from_proto(proto.stop_limit)

        take_profit_price = None
        if proto.take_profit_price > 0:
            take_profit_price = decimal_from_proto(proto.take_profit_price)

        return cls(
            stop_loss=stop_loss,
            take_profit_price=take_profit_price,
        )


class OrderBuilder:
    """Fluent builder for creating order requests.

    Provides a convenient API for constructing complex orders with validation.

    Examples:
        >>> # Simple market buy
        >>> order = OrderBuilder().symbol("AAPL").buy().quantity(100).build()

        >>> # Limit order with stop loss
        >>> order = (OrderBuilder()
        ...     .symbol("AAPL")
        ...     .buy()
        ...     .limit(150.00)
        ...     .quantity(100)
        ...     .with_stop_loss(145.00)
        ...     .build())

        >>> # Bracket order
        >>> order = (OrderBuilder()
        ...     .symbol("AAPL")
        ...     .sell()
        ...     .limit(155.00)
        ...     .quantity(100)
        ...     .with_bracket(stop_loss=150.00, take_profit=160.00)
        ...     .build())
    """

    def __init__(self) -> None:
        """Initialize builder with defaults."""
        self._symbol: Optional[str] = None
        self._side: Optional[OrderSide] = None
        self._order_type: OrderType = OrderType.MARKET
        self._quantity: Optional[Decimal] = None
        self._limit_price: Optional[Decimal] = None
        self._stop_price: Optional[Decimal] = None
        self._time_in_force: TimeInForce = TimeInForce.DAY
        self._order_intent: OrderIntent = OrderIntent.OPEN
        self._client_order_id: Optional[str] = None
        self._parent_trade_id: Optional[str] = None
        self._protective_orders: Optional[ProtectiveOrdersOnFill] = None
        self._metadata: Dict[str, str] = {}

    def symbol(self, symbol: str) -> OrderBuilder:
        """Set the trading symbol.

        Args:
            symbol: Trading symbol (e.g., "AAPL")

        Returns:
            Self for chaining
        """
        self._symbol = symbol
        return self

    def buy(self) -> OrderBuilder:
        """Set order side to BUY.

        Returns:
            Self for chaining
        """
        self._side = OrderSide.BUY
        return self

    def sell(self) -> OrderBuilder:
        """Set order side to SELL.

        Returns:
            Self for chaining
        """
        self._side = OrderSide.SELL
        return self

    def side(self, side: Union[OrderSide, str]) -> OrderBuilder:
        """Set order side.

        Args:
            side: Order side (BUY/SELL)

        Returns:
            Self for chaining
        """
        if isinstance(side, str):
            self._side = OrderSide.from_string(side)
        else:
            self._side = side
        return self

    def quantity(self, quantity: Union[Decimal, int, float]) -> OrderBuilder:
        """Set order quantity.

        Args:
            quantity: Number of shares/units

        Returns:
            Self for chaining
        """
        self._quantity = Decimal(str(quantity))
        return self

    def market(self) -> OrderBuilder:
        """Set order type to MARKET.

        Returns:
            Self for chaining
        """
        self._order_type = OrderType.MARKET
        self._limit_price = None
        self._stop_price = None
        return self

    def limit(self, price: Union[Decimal, int, float]) -> OrderBuilder:
        """Set order type to LIMIT with price.

        Args:
            price: Limit price

        Returns:
            Self for chaining
        """
        self._order_type = OrderType.LIMIT
        self._limit_price = Decimal(str(price))
        return self

    def stop(self, price: Union[Decimal, int, float]) -> OrderBuilder:
        """Set order type to STOP with price.

        Args:
            price: Stop price

        Returns:
            Self for chaining
        """
        self._order_type = OrderType.STOP
        self._stop_price = Decimal(str(price))
        self._limit_price = None
        return self

    def stop_limit(
        self,
        stop_price: Union[Decimal, int, float],
        limit_price: Union[Decimal, int, float],
    ) -> OrderBuilder:
        """Set order type to STOP_LIMIT with prices.

        Args:
            stop_price: Stop trigger price
            limit_price: Limit price after stop triggers

        Returns:
            Self for chaining
        """
        self._order_type = OrderType.STOP_LIMIT
        self._stop_price = Decimal(str(stop_price))
        self._limit_price = Decimal(str(limit_price))
        return self

    def time_in_force(self, tif: Union[TimeInForce, str]) -> OrderBuilder:
        """Set time in force.

        Args:
            tif: Time in force (DAY/GTC/IOC/FOK)

        Returns:
            Self for chaining
        """
        if isinstance(tif, str):
            self._time_in_force = TimeInForce.from_string(tif)
        else:
            self._time_in_force = tif
        return self

    def day(self) -> OrderBuilder:
        """Set time in force to DAY.

        Returns:
            Self for chaining
        """
        self._time_in_force = TimeInForce.DAY
        return self

    def gtc(self) -> OrderBuilder:
        """Set time in force to GTC (Good Till Canceled).

        Returns:
            Self for chaining
        """
        self._time_in_force = TimeInForce.GTC
        return self

    def ioc(self) -> OrderBuilder:
        """Set time in force to IOC (Immediate Or Cancel).

        Returns:
            Self for chaining
        """
        self._time_in_force = TimeInForce.IOC
        return self

    def fok(self) -> OrderBuilder:
        """Set time in force to FOK (Fill Or Kill).

        Returns:
            Self for chaining
        """
        self._time_in_force = TimeInForce.FOK
        return self

    def intent(self, intent: Union[OrderIntent, str]) -> OrderBuilder:
        """Set order intent.

        Args:
            intent: Order intent (OPEN/CLOSE/STOP_LOSS/TAKE_PROFIT)

        Returns:
            Self for chaining
        """
        if isinstance(intent, str):
            self._order_intent = OrderIntent.from_string(intent)
        else:
            self._order_intent = intent
        return self

    def open_position(self) -> OrderBuilder:
        """Set intent to OPEN (opening a new position).

        Returns:
            Self for chaining
        """
        self._order_intent = OrderIntent.OPEN
        return self

    def close_position(self) -> OrderBuilder:
        """Set intent to CLOSE (closing an existing position).

        Returns:
            Self for chaining
        """
        self._order_intent = OrderIntent.CLOSE
        return self

    def client_order_id(self, client_id: str) -> OrderBuilder:
        """Set client order ID.

        Args:
            client_id: Client-assigned order ID

        Returns:
            Self for chaining
        """
        self._client_order_id = client_id
        return self

    def parent_trade(self, trade_id: str) -> OrderBuilder:
        """Set parent trade ID for protective orders.

        Args:
            trade_id: Parent trade ID

        Returns:
            Self for chaining
        """
        self._parent_trade_id = trade_id
        return self

    def with_stop_loss(self, stop_price: Union[Decimal, int, float]) -> OrderBuilder:
        """Add stop loss to be created on fill.

        Args:
            stop_price: Stop loss price

        Returns:
            Self for chaining
        """
        if self._protective_orders is None:
            self._protective_orders = ProtectiveOrdersOnFill()

        self._protective_orders = ProtectiveOrdersOnFill(
            stop_loss=StopOrder(stop_price=Decimal(str(stop_price))),
            take_profit_price=self._protective_orders.take_profit_price,
        )
        return self

    def with_stop_limit(
        self,
        stop_price: Union[Decimal, int, float],
        limit_price: Union[Decimal, int, float],
    ) -> OrderBuilder:
        """Add stop limit order to be created on fill.

        Args:
            stop_price: Stop trigger price
            limit_price: Limit price after trigger

        Returns:
            Self for chaining
        """
        if self._protective_orders is None:
            self._protective_orders = ProtectiveOrdersOnFill()

        self._protective_orders = ProtectiveOrdersOnFill(
            stop_loss=StopLimitOrder(
                stop_price=Decimal(str(stop_price)),
                limit_price=Decimal(str(limit_price)),
            ),
            take_profit_price=self._protective_orders.take_profit_price,
        )
        return self

    def with_take_profit(self, price: Union[Decimal, int, float]) -> OrderBuilder:
        """Add take profit order to be created on fill.

        Args:
            price: Take profit price

        Returns:
            Self for chaining
        """
        if self._protective_orders is None:
            self._protective_orders = ProtectiveOrdersOnFill()

        self._protective_orders = ProtectiveOrdersOnFill(
            stop_loss=self._protective_orders.stop_loss if self._protective_orders else None,
            take_profit_price=Decimal(str(price)),
        )
        return self

    def with_bracket(
        self,
        stop_loss: Union[Decimal, int, float],
        take_profit: Union[Decimal, int, float],
    ) -> OrderBuilder:
        """Add bracket orders (stop loss and take profit) on fill.

        Args:
            stop_loss: Stop loss price
            take_profit: Take profit price

        Returns:
            Self for chaining
        """
        self._protective_orders = ProtectiveOrdersOnFill(
            stop_loss=StopOrder(stop_price=Decimal(str(stop_loss))),
            take_profit_price=Decimal(str(take_profit)),
        )
        return self

    def metadata(self, key: str, value: str) -> OrderBuilder:
        """Add metadata key-value pair.

        Args:
            key: Metadata key
            value: Metadata value

        Returns:
            Self for chaining
        """
        self._metadata[key] = value
        return self

    def build(self) -> orders_pb2.PlaceOrderRequest:
        """Build the order request.

        Returns:
            PlaceOrderRequest proto message

        Raises:
            ValueError: If required fields are missing or invalid
        """
        # Validate required fields
        if not self._symbol:
            raise ValueError("Symbol is required")
        if self._side is None:
            raise ValueError("Side is required")
        if self._quantity is None or self._quantity <= 0:
            raise ValueError("Quantity must be positive")

        # Validate prices based on order type
        if self._order_type.requires_limit_price() and not self._limit_price:
            raise ValueError(f"{self._order_type} requires limit price")
        if self._order_type.requires_stop_price() and not self._stop_price:
            raise ValueError(f"{self._order_type} requires stop price")

        # Build request
        request = orders_pb2.PlaceOrderRequest(
            symbol=self._symbol,
            side=self._side.to_proto(),
            order_type=self._order_type.to_proto(),
            quantity=proto_from_decimal(self._quantity),
            time_in_force=self._time_in_force.to_proto(),
            order_intent=self._order_intent.to_proto(),
        )

        # Set optional fields
        if self._limit_price:
            request.limit_price = proto_from_decimal(self._limit_price)
        if self._stop_price:
            request.stop_price = proto_from_decimal(self._stop_price)
        if self._client_order_id:
            request.client_order_id = self._client_order_id
        if self._parent_trade_id:
            request.parent_trade_id = self._parent_trade_id
        if self._protective_orders:
            request.protective_orders_on_fill.CopyFrom(self._protective_orders.to_proto())
        if self._metadata:
            request.metadata.update(self._metadata)

        return request
