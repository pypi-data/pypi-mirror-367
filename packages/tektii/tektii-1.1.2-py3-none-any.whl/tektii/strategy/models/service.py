"""Service request/response models for strategy-broker communication.

This module contains models for all service method requests and responses,
enabling strategies to query state and manage orders through the broker.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

from tektii.strategy.grpc import market_data_pb2, orders_pb2
from tektii.strategy.models.common import AccountState, Bar, Position, PriceLevel
from tektii.strategy.models.conversions import decimal_from_proto, decimal_from_proto_required, proto_from_decimal
from tektii.strategy.models.enums import OrderIntent, OrderSide, OrderStatus, OrderType, TimeInForce
from tektii.strategy.models.errors import RejectCode
from tektii.strategy.models.orders import Order, ProtectiveOrdersOnFill
from tektii.strategy.models.risk import PositionRisk, RiskCheckResult, ValidationError, ValidationWarning

# Lifecycle Messages


class InitRequest(BaseModel):
    """Strategy initialization parameters.

    Sent to strategy when it starts up, containing configuration
    and symbols to trade.
    """

    config: Dict[str, str] = Field(default_factory=dict, description="Strategy configuration parameters")
    symbols: List[str] = Field(default_factory=list, description="Symbols to trade")
    strategy_id: str = Field(..., description="Unique strategy identifier")

    class Config:
        """Pydantic model configuration."""

        frozen = True

    def to_proto(self) -> orders_pb2.InitRequest:
        """Convert to proto message."""
        return orders_pb2.InitRequest(
            config=self.config,
            symbols=self.symbols,
            strategy_id=self.strategy_id,
        )

    @classmethod
    def from_proto(cls, proto: orders_pb2.InitRequest) -> InitRequest:
        """Create from proto message."""
        return cls(
            config=dict(proto.config) if proto.config else {},
            symbols=list(proto.symbols),
            strategy_id=proto.strategy_id,
        )


class InitResponse(BaseModel):
    """Strategy initialization response.

    Confirms successful initialization and reports strategy capabilities.
    """

    success: bool = Field(..., description="Whether initialization succeeded")
    message: str = Field("", description="Success/error message")
    capabilities: Dict[str, str] = Field(default_factory=dict, description="Strategy capabilities")

    class Config:
        """Pydantic model configuration."""

        frozen = True

    def to_proto(self) -> orders_pb2.InitResponse:
        """Convert to proto message."""
        return orders_pb2.InitResponse(
            success=self.success,
            message=self.message,
            capabilities=self.capabilities,
        )

    @classmethod
    def from_proto(cls, proto: orders_pb2.InitResponse) -> InitResponse:
        """Create from proto message."""
        return cls(
            success=proto.success,
            message=proto.message,
            capabilities=dict(proto.capabilities) if proto.capabilities else {},
        )


class ShutdownRequest(BaseModel):
    """Strategy shutdown request.

    Initiates graceful shutdown of the strategy.
    """

    reason: str = Field("", description="Shutdown reason")
    force: bool = Field(False, description="Force immediate shutdown")

    class Config:
        """Pydantic model configuration."""

        frozen = True

    def to_proto(self) -> orders_pb2.ShutdownRequest:
        """Convert to proto message."""
        return orders_pb2.ShutdownRequest(
            reason=self.reason,
            force=self.force,
        )

    @classmethod
    def from_proto(cls, proto: orders_pb2.ShutdownRequest) -> ShutdownRequest:
        """Create from proto message."""
        return cls(
            reason=proto.reason,
            force=proto.force,
        )


class ShutdownResponse(BaseModel):
    """Strategy shutdown response.

    Confirms shutdown completion.
    """

    success: bool = Field(..., description="Whether shutdown succeeded")
    message: str = Field("", description="Success/error message")

    class Config:
        """Pydantic model configuration."""

        frozen = True

    def to_proto(self) -> orders_pb2.ShutdownResponse:
        """Convert to proto message."""
        return orders_pb2.ShutdownResponse(
            success=self.success,
            message=self.message,
        )

    @classmethod
    def from_proto(cls, proto: orders_pb2.ShutdownResponse) -> ShutdownResponse:
        """Create from proto message."""
        return cls(
            success=proto.success,
            message=proto.message,
        )


class ProcessEventResponse(BaseModel):
    """Response after processing an event.

    Acknowledges event processing and can include metadata.
    """

    success: bool = Field(True, description="Whether event was processed successfully")
    error: str = Field("", description="Error message if processing failed")
    metadata: Dict[str, str] = Field(default_factory=dict, description="Response metadata")

    class Config:
        """Pydantic model configuration."""

        frozen = True

    def to_proto(self) -> orders_pb2.ProcessEventResponse:
        """Convert to proto message."""
        return orders_pb2.ProcessEventResponse(
            success=self.success,
            error=self.error,
            metadata=self.metadata,
        )

    @classmethod
    def from_proto(cls, proto: orders_pb2.ProcessEventResponse) -> ProcessEventResponse:
        """Create from proto message."""
        return cls(
            success=proto.success,
            error=proto.error,
            metadata=dict(proto.metadata) if proto.metadata else {},
        )


# Query Messages


class StateRequest(BaseModel):
    """Request current strategy state.

    Queries positions, orders, and account information.
    """

    symbols: List[str] = Field(default_factory=list, description="Symbols to query (empty = all)")
    include_positions: bool = Field(True, description="Include position data")
    include_orders: bool = Field(True, description="Include order data")
    include_account: bool = Field(True, description="Include account data")

    class Config:
        """Pydantic model configuration."""

        frozen = True

    def to_proto(self) -> orders_pb2.StateRequest:
        """Convert to proto message."""
        return orders_pb2.StateRequest(
            symbols=self.symbols,
            include_positions=self.include_positions,
            include_orders=self.include_orders,
            include_account=self.include_account,
        )

    @classmethod
    def from_proto(cls, proto: orders_pb2.StateRequest) -> StateRequest:
        """Create from proto message."""
        return cls(
            symbols=list(proto.symbols),
            include_positions=proto.include_positions,
            include_orders=proto.include_orders,
            include_account=proto.include_account,
        )


class StateResponse(BaseModel):
    """Current state snapshot.

    Contains positions, orders, and account state as requested.
    """

    positions: Dict[str, Position] = Field(default_factory=dict, description="Positions by symbol")
    orders: Dict[str, Order] = Field(default_factory=dict, description="Orders by order_id")
    account: Optional[AccountState] = Field(None, description="Account state")
    timestamp_us: int = Field(..., description="Snapshot timestamp (microseconds)")

    class Config:
        """Pydantic model configuration."""

        frozen = True
        arbitrary_types_allowed = True

    @property
    def timestamp(self) -> datetime:
        """Get snapshot timestamp as datetime."""
        return datetime.fromtimestamp(self.timestamp_us / 1_000_000)

    def to_proto(self) -> orders_pb2.StateResponse:
        """Convert to proto message."""
        proto = orders_pb2.StateResponse(
            timestamp_us=self.timestamp_us,
        )

        for symbol, position in self.positions.items():
            proto.positions[symbol].CopyFrom(position.to_proto())

        for order_id, order in self.orders.items():
            proto.orders[order_id].CopyFrom(order.to_proto())

        if self.account is not None:
            proto.account.CopyFrom(self.account.to_proto())

        return proto

    @classmethod
    def from_proto(cls, proto: orders_pb2.StateResponse) -> StateResponse:
        """Create from proto message."""
        positions = {symbol: Position.from_proto(pos_proto) for symbol, pos_proto in proto.positions.items()}

        orders = {order_id: Order.from_proto(order_proto) for order_id, order_proto in proto.orders.items()}

        account = None
        if proto.HasField("account"):
            account = AccountState.from_proto(proto.account)

        return cls(
            positions=positions,
            orders=orders,
            account=account,
            timestamp_us=proto.timestamp_us,
        )


class HistoricalDataRequest(BaseModel):
    """Request historical bar data.

    Queries historical OHLCV data for analysis.
    """

    symbol: str = Field(..., description="Symbol to query")
    start_timestamp_us: int = Field(..., description="Start time (microseconds since epoch)")
    end_timestamp_us: int = Field(..., description="End time (microseconds since epoch)")
    bar_size: str = Field("1min", description="Bar size (1min, 5min, 15min, 30min, 1hour, 4hour, 1day)")
    limit: int = Field(1000, description="Maximum bars to return (1-10000)")

    class Config:
        """Pydantic model configuration."""

        frozen = True

    @property
    def start_datetime(self) -> datetime:
        """Get start time as datetime."""
        return datetime.fromtimestamp(self.start_timestamp_us / 1_000_000)

    @property
    def end_datetime(self) -> datetime:
        """Get end time as datetime."""
        return datetime.fromtimestamp(self.end_timestamp_us / 1_000_000)

    def to_proto(self) -> market_data_pb2.HistoricalDataRequest:
        """Convert to proto message."""
        return market_data_pb2.HistoricalDataRequest(
            symbol=self.symbol,
            start_timestamp_us=self.start_timestamp_us,
            end_timestamp_us=self.end_timestamp_us,
            bar_size=self.bar_size,
            limit=self.limit,
        )

    @classmethod
    def from_proto(cls, proto: market_data_pb2.HistoricalDataRequest) -> HistoricalDataRequest:
        """Create from proto message."""
        return cls(
            symbol=proto.symbol,
            start_timestamp_us=proto.start_timestamp_us,
            end_timestamp_us=proto.end_timestamp_us,
            bar_size=proto.bar_size,
            limit=proto.limit,
        )


class HistoricalDataResponse(BaseModel):
    """Historical bar data response.

    Contains requested historical OHLCV bars.
    """

    symbol: str = Field(..., description="Symbol")
    bar_size: str = Field(..., description="Bar size")
    bars: List[Bar] = Field(default_factory=list, description="Historical bars")

    class Config:
        """Pydantic model configuration."""

        frozen = True
        arbitrary_types_allowed = True

    def to_proto(self) -> market_data_pb2.HistoricalDataResponse:
        """Convert to proto message."""
        proto = market_data_pb2.HistoricalDataResponse(
            symbol=self.symbol,
            bar_size=self.bar_size,
        )

        for bar in self.bars:
            proto.bars.append(bar.to_proto())

        return proto

    @classmethod
    def from_proto(cls, proto: market_data_pb2.HistoricalDataResponse) -> HistoricalDataResponse:
        """Create from proto message."""
        bars = [Bar.from_proto(bar_proto) for bar_proto in proto.bars]

        return cls(
            symbol=proto.symbol,
            bar_size=proto.bar_size,
            bars=bars,
        )


class MarketDepthRequest(BaseModel):
    """Request order book data.

    Queries current bid/ask levels.
    """

    symbol: str = Field(..., description="Symbol to query")
    depth: int = Field(10, description="Number of price levels")

    class Config:
        """Pydantic model configuration."""

        frozen = True

    def to_proto(self) -> market_data_pb2.MarketDepthRequest:
        """Convert to proto message."""
        return market_data_pb2.MarketDepthRequest(
            symbol=self.symbol,
            depth=self.depth,
        )

    @classmethod
    def from_proto(cls, proto: market_data_pb2.MarketDepthRequest) -> MarketDepthRequest:
        """Create from proto message."""
        return cls(
            symbol=proto.symbol,
            depth=proto.depth,
        )


class MarketDepthResponse(BaseModel):
    """Current order book snapshot.

    Contains bid and ask levels.
    """

    symbol: str = Field(..., description="Symbol")
    timestamp_us: int = Field(..., description="Snapshot timestamp")
    bids: List[PriceLevel] = Field(default_factory=list, description="Bid levels (sorted by price desc)")
    asks: List[PriceLevel] = Field(default_factory=list, description="Ask levels (sorted by price asc)")

    class Config:
        """Pydantic model configuration."""

        frozen = True
        arbitrary_types_allowed = True

    @property
    def timestamp(self) -> datetime:
        """Get snapshot timestamp as datetime."""
        return datetime.fromtimestamp(self.timestamp_us / 1_000_000)

    @property
    def best_bid(self) -> Optional[PriceLevel]:
        """Get best (highest) bid."""
        return self.bids[0] if self.bids else None

    @property
    def best_ask(self) -> Optional[PriceLevel]:
        """Get best (lowest) ask."""
        return self.asks[0] if self.asks else None

    @property
    def spread(self) -> Optional[Decimal]:
        """Calculate bid-ask spread."""
        if self.best_bid and self.best_ask:
            return self.best_ask.price - self.best_bid.price
        return None

    def to_proto(self) -> market_data_pb2.MarketDepthResponse:
        """Convert to proto message."""
        proto = market_data_pb2.MarketDepthResponse(
            symbol=self.symbol,
            timestamp_us=self.timestamp_us,
        )

        for bid in self.bids:
            proto.bids.append(bid.to_proto())

        for ask in self.asks:
            proto.asks.append(ask.to_proto())

        return proto

    @classmethod
    def from_proto(cls, proto: market_data_pb2.MarketDepthResponse) -> MarketDepthResponse:
        """Create from proto message."""
        bids = [PriceLevel.from_proto(bid_proto) for bid_proto in proto.bids]
        asks = [PriceLevel.from_proto(ask_proto) for ask_proto in proto.asks]

        return cls(
            symbol=proto.symbol,
            timestamp_us=proto.timestamp_us,
            bids=bids,
            asks=asks,
        )


class RiskMetricsRequest(BaseModel):
    """Request portfolio risk metrics.

    Queries risk calculations like VaR and correlations.
    """

    symbols: List[str] = Field(default_factory=list, description="Symbols to analyze (empty = all)")
    confidence_level: Decimal = Field(Decimal("0.95"), description="VaR confidence level")
    lookback_days: int = Field(252, description="Historical period for calculations")

    class Config:
        """Pydantic model configuration."""

        frozen = True
        arbitrary_types_allowed = True

    @field_validator("confidence_level")
    @classmethod
    def validate_confidence(cls, v: Any) -> Decimal:
        """Ensure confidence level is Decimal between 0 and 1."""
        if isinstance(v, (int, float, str)):
            v = Decimal(str(v))
        elif not isinstance(v, Decimal):
            raise ValueError(f"Cannot convert {type(v)} to Decimal")
        if not (0 < v < 1):
            raise ValueError("Confidence level must be between 0 and 1")
        return v  # type: ignore[no-any-return]

    def to_proto(self) -> orders_pb2.RiskMetricsRequest:
        """Convert to proto message."""
        return orders_pb2.RiskMetricsRequest(
            symbols=self.symbols,
            confidence_level=proto_from_decimal(self.confidence_level),
            lookback_days=self.lookback_days,
        )

    @classmethod
    def from_proto(cls, proto: orders_pb2.RiskMetricsRequest) -> RiskMetricsRequest:
        """Create from proto message."""
        return cls(
            symbols=list(proto.symbols),
            confidence_level=decimal_from_proto_required(proto.confidence_level),
            lookback_days=proto.lookback_days,
        )


class RiskMetricsResponse(BaseModel):
    """Portfolio risk calculations.

    Contains VaR, Sharpe, correlations, and position-level risks.
    """

    # Portfolio-level metrics
    portfolio_var: Decimal = Field(..., description="Portfolio Value at Risk")
    portfolio_sharpe: Decimal = Field(..., description="Portfolio Sharpe ratio")
    portfolio_beta: Decimal = Field(..., description="Portfolio beta vs market")
    max_drawdown: Decimal = Field(..., description="Maximum drawdown")

    # Position-level metrics
    position_risks: Dict[str, PositionRisk] = Field(default_factory=dict, description="Risk by position")

    # Correlation matrix (symbol pairs as keys like "AAPL,MSFT")
    correlations: Dict[str, Decimal] = Field(default_factory=dict, description="Pairwise correlations")

    timestamp_us: int = Field(..., description="Calculation timestamp")

    class Config:
        """Pydantic model configuration."""

        frozen = True
        arbitrary_types_allowed = True

    @field_validator("portfolio_var", "portfolio_sharpe", "portfolio_beta", "max_drawdown")
    @classmethod
    def validate_decimal(cls, v: Any) -> Decimal:
        """Ensure all numeric fields are Decimal."""
        if isinstance(v, (int, float, str)):
            return Decimal(str(v))
        if isinstance(v, Decimal):
            return v
        raise ValueError(f"Cannot convert {type(v)} to Decimal")

    @field_validator("correlations")
    @classmethod
    def validate_correlations(cls, v: Dict[str, Any]) -> Dict[str, Decimal]:
        """Ensure correlation values are Decimal."""
        result = {}
        for key, value in v.items():
            if isinstance(value, (int, float, str)):
                result[key] = Decimal(str(value))
            elif isinstance(value, Decimal):
                result[key] = value
        return result

    @property
    def timestamp(self) -> datetime:
        """Get calculation timestamp as datetime."""
        return datetime.fromtimestamp(self.timestamp_us / 1_000_000)

    def to_proto(self) -> orders_pb2.RiskMetricsResponse:
        """Convert to proto message."""
        proto = orders_pb2.RiskMetricsResponse(
            portfolio_var=proto_from_decimal(self.portfolio_var),
            portfolio_sharpe=proto_from_decimal(self.portfolio_sharpe),
            portfolio_beta=proto_from_decimal(self.portfolio_beta),
            max_drawdown=proto_from_decimal(self.max_drawdown),
            timestamp_us=self.timestamp_us,
        )

        for symbol, risk in self.position_risks.items():
            proto.position_risks[symbol].CopyFrom(risk.to_proto())

        for pair, corr in self.correlations.items():
            proto.correlations[pair] = proto_from_decimal(corr)

        return proto

    @classmethod
    def from_proto(cls, proto: orders_pb2.RiskMetricsResponse) -> RiskMetricsResponse:
        """Create from proto message."""
        position_risks = {symbol: PositionRisk.from_proto(risk_proto) for symbol, risk_proto in proto.position_risks.items()}

        correlations = {pair: decimal_from_proto_required(corr) for pair, corr in proto.correlations.items()}

        return cls(
            portfolio_var=decimal_from_proto_required(proto.portfolio_var),
            portfolio_sharpe=decimal_from_proto_required(proto.portfolio_sharpe),
            portfolio_beta=decimal_from_proto_required(proto.portfolio_beta),
            max_drawdown=decimal_from_proto_required(proto.max_drawdown),
            position_risks=position_risks,
            correlations=correlations,
            timestamp_us=proto.timestamp_us,
        )


# Order Management Messages


class PlaceOrderRequest(BaseModel):
    """Submit a new order.

    Contains all order parameters including type, quantity, prices,
    and optional protective orders.
    """

    symbol: str = Field(..., description="Trading symbol")
    side: OrderSide = Field(..., description="Buy or sell")
    order_type: OrderType = Field(..., description="Order type")
    quantity: Decimal = Field(..., description="Order quantity")

    # Prices (required based on order type)
    limit_price: Optional[Decimal] = Field(None, description="Limit price")
    stop_price: Optional[Decimal] = Field(None, description="Stop trigger price")

    # Order parameters
    time_in_force: TimeInForce = Field(TimeInForce.DAY, description="Order duration")
    client_order_id: Optional[str] = Field(None, description="Client-assigned ID")
    metadata: Dict[str, str] = Field(default_factory=dict, description="Order metadata")

    # Order intent and relationships
    order_intent: OrderIntent = Field(OrderIntent.UNKNOWN, description="Order purpose")
    parent_trade_id: Optional[str] = Field(None, description="Parent trade ID for protective orders")

    # Automatic protective orders on fill
    protective_orders_on_fill: Optional[ProtectiveOrdersOnFill] = Field(None, description="Create protective orders when filled")

    # Request tracking
    request_id: Optional[str] = Field(None, description="Request correlation ID")
    validate_only: bool = Field(False, description="Perform validation only")

    class Config:
        """Pydantic model configuration."""

        frozen = True
        arbitrary_types_allowed = True

    @field_validator("quantity", "limit_price", "stop_price")
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

    def validate_prices(self) -> List[str]:
        """Validate required prices based on order type.

        Returns:
            List of validation errors
        """
        errors = []

        if self.order_type == OrderType.LIMIT and self.limit_price is None:
            errors.append("Limit price required for limit orders")

        if self.order_type in [OrderType.STOP, OrderType.STOP_LIMIT] and self.stop_price is None:
            errors.append("Stop price required for stop orders")

        if self.order_type == OrderType.STOP_LIMIT and self.limit_price is None:
            errors.append("Limit price required for stop limit orders")

        return errors

    def to_proto(self) -> orders_pb2.PlaceOrderRequest:
        """Convert to proto message."""
        proto = orders_pb2.PlaceOrderRequest(
            symbol=self.symbol,
            side=self.side.to_proto(),
            order_type=self.order_type.to_proto(),
            quantity=proto_from_decimal(self.quantity),
            limit_price=proto_from_decimal(self.limit_price),
            stop_price=proto_from_decimal(self.stop_price),
            time_in_force=self.time_in_force.to_proto(),
            client_order_id=self.client_order_id or "",
            metadata=self.metadata,
            order_intent=self.order_intent.to_proto(),
            parent_trade_id=self.parent_trade_id or "",
            request_id=self.request_id or "",
            validate_only=self.validate_only,
        )

        if self.protective_orders_on_fill is not None:
            proto.protective_orders_on_fill.CopyFrom(self.protective_orders_on_fill.to_proto())

        return proto

    @classmethod
    def from_proto(cls, proto: orders_pb2.PlaceOrderRequest) -> PlaceOrderRequest:
        """Create from proto message."""
        protective_orders = None
        if proto.HasField("protective_orders_on_fill"):
            protective_orders = ProtectiveOrdersOnFill.from_proto(proto.protective_orders_on_fill)

        return cls(
            symbol=proto.symbol,
            side=OrderSide.from_proto(proto.side),
            order_type=OrderType.from_proto(proto.order_type),
            quantity=decimal_from_proto_required(proto.quantity),
            limit_price=decimal_from_proto(proto.limit_price),
            stop_price=decimal_from_proto(proto.stop_price),
            time_in_force=TimeInForce.from_proto(proto.time_in_force),
            client_order_id=proto.client_order_id if proto.client_order_id else None,
            metadata=dict(proto.metadata) if proto.metadata else {},
            order_intent=OrderIntent.from_proto(proto.order_intent),
            parent_trade_id=proto.parent_trade_id if proto.parent_trade_id else None,
            protective_orders_on_fill=protective_orders,
            request_id=proto.request_id if proto.request_id else None,
            validate_only=proto.validate_only,
        )


class PlaceOrderResponse(BaseModel):
    """Order placement response.

    Provides immediate feedback on order acceptance or rejection.
    """

    accepted: bool = Field(..., description="Whether order was accepted")
    order_id: Optional[str] = Field(None, description="Broker-assigned order ID")
    request_id: Optional[str] = Field(None, description="Echo of request correlation ID")

    # Rejection details
    reject_reason: Optional[str] = Field(None, description="Rejection reason")
    reject_code: Optional[RejectCode] = Field(None, description="Rejection code")

    # Risk check results
    risk_check: Optional[RiskCheckResult] = Field(None, description="Pre-trade risk analysis")

    # Estimates
    estimated_fill_price: Optional[Decimal] = Field(None, description="Estimated execution price")
    estimated_commission: Optional[Decimal] = Field(None, description="Estimated commission")

    timestamp_us: int = Field(..., description="Response timestamp")

    class Config:
        """Pydantic model configuration."""

        frozen = True
        arbitrary_types_allowed = True

    @field_validator("estimated_fill_price", "estimated_commission")
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
    def timestamp(self) -> datetime:
        """Get response timestamp as datetime."""
        return datetime.fromtimestamp(self.timestamp_us / 1_000_000)

    def to_proto(self) -> orders_pb2.PlaceOrderResponse:
        """Convert to proto message."""
        proto = orders_pb2.PlaceOrderResponse(
            accepted=self.accepted,
            order_id=self.order_id or "",
            request_id=self.request_id or "",
            reject_reason=self.reject_reason or "",
            reject_code=self.reject_code.to_proto() if self.reject_code else 0,
            estimated_fill_price=proto_from_decimal(self.estimated_fill_price),
            estimated_commission=proto_from_decimal(self.estimated_commission),
            timestamp_us=self.timestamp_us,
        )

        if self.risk_check is not None:
            proto.risk_check.CopyFrom(self.risk_check.to_proto())

        return proto

    @classmethod
    def from_proto(cls, proto: orders_pb2.PlaceOrderResponse) -> PlaceOrderResponse:
        """Create from proto message."""
        risk_check = None
        if proto.HasField("risk_check"):
            risk_check = RiskCheckResult.from_proto(proto.risk_check)

        reject_code = None
        if proto.reject_code != 0:
            reject_code = RejectCode.from_proto(proto.reject_code)

        return cls(
            accepted=proto.accepted,
            order_id=proto.order_id if proto.order_id else None,
            request_id=proto.request_id if proto.request_id else None,
            reject_reason=proto.reject_reason if proto.reject_reason else None,
            reject_code=reject_code,
            risk_check=risk_check,
            estimated_fill_price=decimal_from_proto(proto.estimated_fill_price),
            estimated_commission=decimal_from_proto(proto.estimated_commission),
            timestamp_us=proto.timestamp_us,
        )


class CancelOrderRequest(BaseModel):
    """Cancel an existing order.

    Requests cancellation of a pending order.
    """

    order_id: str = Field(..., description="Order ID to cancel")
    request_id: Optional[str] = Field(None, description="Request correlation ID")

    class Config:
        """Pydantic model configuration."""

        frozen = True

    def to_proto(self) -> orders_pb2.CancelOrderRequest:
        """Convert to proto message."""
        return orders_pb2.CancelOrderRequest(
            order_id=self.order_id,
            request_id=self.request_id or "",
        )

    @classmethod
    def from_proto(cls, proto: orders_pb2.CancelOrderRequest) -> CancelOrderRequest:
        """Create from proto message."""
        return cls(
            order_id=proto.order_id,
            request_id=proto.request_id if proto.request_id else None,
        )


class CancelOrderResponse(BaseModel):
    """Order cancellation response.

    Confirms cancellation or provides rejection reason.
    """

    accepted: bool = Field(..., description="Whether cancellation was accepted")
    order_id: str = Field(..., description="Order ID")
    request_id: Optional[str] = Field(None, description="Echo of request ID")

    reject_reason: Optional[str] = Field(None, description="Rejection reason")
    reject_code: Optional[RejectCode] = Field(None, description="Rejection code")

    # State at cancellation
    previous_status: Optional[OrderStatus] = Field(None, description="Order status before cancel")
    filled_quantity: Optional[Decimal] = Field(None, description="Quantity filled before cancel")

    timestamp_us: int = Field(..., description="Response timestamp")

    class Config:
        """Pydantic model configuration."""

        frozen = True
        arbitrary_types_allowed = True

    @field_validator("filled_quantity")
    @classmethod
    def validate_decimal(cls, v: Any) -> Optional[Decimal]:
        """Ensure filled quantity is Decimal."""
        if v is None:
            return None
        if isinstance(v, (int, float, str)):
            return Decimal(str(v))
        if isinstance(v, Decimal):
            return v
        raise ValueError(f"Cannot convert {type(v)} to Decimal")

    @property
    def timestamp(self) -> datetime:
        """Get response timestamp as datetime."""
        return datetime.fromtimestamp(self.timestamp_us / 1_000_000)

    def to_proto(self) -> orders_pb2.CancelOrderResponse:
        """Convert to proto message."""
        return orders_pb2.CancelOrderResponse(
            accepted=self.accepted,
            order_id=self.order_id,
            request_id=self.request_id or "",
            reject_reason=self.reject_reason or "",
            reject_code=self.reject_code.to_proto() if self.reject_code else 0,
            previous_status=self.previous_status.to_proto() if self.previous_status else 0,
            filled_quantity=proto_from_decimal(self.filled_quantity),
            timestamp_us=self.timestamp_us,
        )

    @classmethod
    def from_proto(cls, proto: orders_pb2.CancelOrderResponse) -> CancelOrderResponse:
        """Create from proto message."""
        reject_code = None
        if proto.reject_code != 0:
            reject_code = RejectCode.from_proto(proto.reject_code)

        previous_status = None
        if proto.previous_status != 0:
            previous_status = OrderStatus.from_proto(proto.previous_status)

        return cls(
            accepted=proto.accepted,
            order_id=proto.order_id,
            request_id=proto.request_id if proto.request_id else None,
            reject_reason=proto.reject_reason if proto.reject_reason else None,
            reject_code=reject_code,
            previous_status=previous_status,
            filled_quantity=decimal_from_proto(proto.filled_quantity),
            timestamp_us=proto.timestamp_us,
        )


class ValidateOrderRequest(BaseModel):
    """Pre-trade order validation.

    Checks if an order would be accepted without placing it.
    """

    symbol: str = Field(..., description="Trading symbol")
    side: OrderSide = Field(..., description="Buy or sell")
    order_type: OrderType = Field(..., description="Order type")
    quantity: Decimal = Field(..., description="Order quantity")
    limit_price: Optional[Decimal] = Field(None, description="Limit price")
    stop_price: Optional[Decimal] = Field(None, description="Stop price")

    request_id: Optional[str] = Field(None, description="Request correlation ID")

    class Config:
        """Pydantic model configuration."""

        frozen = True
        arbitrary_types_allowed = True

    @field_validator("quantity", "limit_price", "stop_price")
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

    def to_proto(self) -> orders_pb2.ValidateOrderRequest:
        """Convert to proto message."""
        return orders_pb2.ValidateOrderRequest(
            symbol=self.symbol,
            side=self.side.to_proto(),
            order_type=self.order_type.to_proto(),
            quantity=proto_from_decimal(self.quantity),
            limit_price=proto_from_decimal(self.limit_price),
            stop_price=proto_from_decimal(self.stop_price),
            request_id=self.request_id or "",
        )

    @classmethod
    def from_proto(cls, proto: orders_pb2.ValidateOrderRequest) -> ValidateOrderRequest:
        """Create from proto message."""
        return cls(
            symbol=proto.symbol,
            side=OrderSide.from_proto(proto.side),
            order_type=OrderType.from_proto(proto.order_type),
            quantity=decimal_from_proto_required(proto.quantity),
            limit_price=decimal_from_proto(proto.limit_price),
            stop_price=decimal_from_proto(proto.stop_price),
            request_id=proto.request_id if proto.request_id else None,
        )


class ValidateOrderResponse(BaseModel):
    """Order validation results.

    Returns validation errors/warnings and risk analysis.
    """

    valid: bool = Field(..., description="Whether order is valid")
    request_id: Optional[str] = Field(None, description="Echo of request ID")

    errors: List[ValidationError] = Field(default_factory=list, description="Validation errors")
    warnings: List[ValidationWarning] = Field(default_factory=list, description="Validation warnings")

    risk_check: Optional[RiskCheckResult] = Field(None, description="Risk analysis")

    # Market impact estimates
    estimated_fill_price: Optional[Decimal] = Field(None, description="Estimated execution price")
    estimated_market_impact: Optional[Decimal] = Field(None, description="Estimated price impact")

    class Config:
        """Pydantic model configuration."""

        frozen = True
        arbitrary_types_allowed = True

    @field_validator("estimated_fill_price", "estimated_market_impact")
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

    def to_proto(self) -> orders_pb2.ValidateOrderResponse:
        """Convert to proto message."""
        proto = orders_pb2.ValidateOrderResponse(
            valid=self.valid,
            request_id=self.request_id or "",
            estimated_fill_price=proto_from_decimal(self.estimated_fill_price),
            estimated_market_impact=proto_from_decimal(self.estimated_market_impact),
        )

        for error in self.errors:
            proto.errors.append(error.to_proto())

        for warning in self.warnings:
            proto.warnings.append(warning.to_proto())

        if self.risk_check is not None:
            proto.risk_check.CopyFrom(self.risk_check.to_proto())

        return proto

    @classmethod
    def from_proto(cls, proto: orders_pb2.ValidateOrderResponse) -> ValidateOrderResponse:
        """Create from proto message."""
        errors = [ValidationError.from_proto(e) for e in proto.errors]
        warnings = [ValidationWarning.from_proto(w) for w in proto.warnings]

        risk_check = None
        if proto.HasField("risk_check"):
            risk_check = RiskCheckResult.from_proto(proto.risk_check)

        return cls(
            valid=proto.valid,
            request_id=proto.request_id if proto.request_id else None,
            errors=errors,
            warnings=warnings,
            risk_check=risk_check,
            estimated_fill_price=decimal_from_proto(proto.estimated_fill_price),
            estimated_market_impact=decimal_from_proto(proto.estimated_market_impact),
        )


class ClosePositionRequest(BaseModel):
    """Close a position.

    Convenience method to close all or part of a position.
    """

    symbol: str = Field(..., description="Symbol to close")
    quantity: Decimal = Field(Decimal(0), description="Quantity to close (0 = entire position)")

    # Order routing preferences
    order_type: OrderType = Field(OrderType.MARKET, description="Order type to use")
    limit_price: Optional[Decimal] = Field(None, description="Limit price for limit orders")

    request_id: Optional[str] = Field(None, description="Request correlation ID")

    class Config:
        """Pydantic model configuration."""

        frozen = True
        arbitrary_types_allowed = True

    @field_validator("quantity", "limit_price")
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

    def to_proto(self) -> orders_pb2.ClosePositionRequest:
        """Convert to proto message."""
        return orders_pb2.ClosePositionRequest(
            symbol=self.symbol,
            quantity=proto_from_decimal(self.quantity),
            order_type=self.order_type.to_proto(),
            limit_price=proto_from_decimal(self.limit_price),
            request_id=self.request_id or "",
        )

    @classmethod
    def from_proto(cls, proto: orders_pb2.ClosePositionRequest) -> ClosePositionRequest:
        """Create from proto message."""
        return cls(
            symbol=proto.symbol,
            quantity=decimal_from_proto_required(proto.quantity),
            order_type=OrderType.from_proto(proto.order_type),
            limit_price=decimal_from_proto(proto.limit_price),
            request_id=proto.request_id if proto.request_id else None,
        )


class ClosePositionResponse(BaseModel):
    """Position closure response.

    Confirms orders created to close the position.
    """

    accepted: bool = Field(..., description="Whether request was accepted")
    request_id: Optional[str] = Field(None, description="Echo of request ID")

    # Created order IDs
    order_ids: List[str] = Field(default_factory=list, description="Created order IDs")

    # Position details
    position_quantity: Decimal = Field(..., description="Current position size")
    closing_quantity: Decimal = Field(..., description="Quantity being closed")
    remaining_quantity: Decimal = Field(..., description="Quantity remaining after close")

    reject_reason: Optional[str] = Field(None, description="Rejection reason")
    reject_code: Optional[RejectCode] = Field(None, description="Rejection code")

    timestamp_us: int = Field(..., description="Response timestamp")

    class Config:
        """Pydantic model configuration."""

        frozen = True
        arbitrary_types_allowed = True

    @field_validator("position_quantity", "closing_quantity", "remaining_quantity")
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
        """Get response timestamp as datetime."""
        return datetime.fromtimestamp(self.timestamp_us / 1_000_000)

    def to_proto(self) -> orders_pb2.ClosePositionResponse:
        """Convert to proto message."""
        return orders_pb2.ClosePositionResponse(
            accepted=self.accepted,
            request_id=self.request_id or "",
            order_ids=self.order_ids,
            position_quantity=proto_from_decimal(self.position_quantity),
            closing_quantity=proto_from_decimal(self.closing_quantity),
            remaining_quantity=proto_from_decimal(self.remaining_quantity),
            reject_reason=self.reject_reason or "",
            reject_code=self.reject_code.to_proto() if self.reject_code else 0,
            timestamp_us=self.timestamp_us,
        )

    @classmethod
    def from_proto(cls, proto: orders_pb2.ClosePositionResponse) -> ClosePositionResponse:
        """Create from proto message."""
        reject_code = None
        if proto.reject_code != 0:
            reject_code = RejectCode.from_proto(proto.reject_code)

        return cls(
            accepted=proto.accepted,
            request_id=proto.request_id if proto.request_id else None,
            order_ids=list(proto.order_ids),
            position_quantity=decimal_from_proto_required(proto.position_quantity),
            closing_quantity=decimal_from_proto_required(proto.closing_quantity),
            remaining_quantity=decimal_from_proto_required(proto.remaining_quantity),
            reject_reason=proto.reject_reason if proto.reject_reason else None,
            reject_code=reject_code,
            timestamp_us=proto.timestamp_us,
        )
