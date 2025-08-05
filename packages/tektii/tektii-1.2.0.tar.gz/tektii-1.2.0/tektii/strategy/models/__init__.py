"""Type-safe models for the Tektii Strategy SDK.

This module provides Pydantic-based models that mirror the proto definitions
with enhanced type safety and developer experience.

Main categories:
- Common: Core trading entities (Position, AccountState, Bar, PriceLevel)
- Enums: Trading enumerations with helper methods
- Orders: Order-related models and builders
- Market Data: Tick, bar, and options data
- Events: Trading and system events
- Service: Request/response models for the API
- Risk: Risk analysis and validation models
"""

# Common models
from tektii.strategy.models.common import AccountState, Bar, Position, PriceLevel

# Enums
from tektii.strategy.models.enums import BarType, OrderIntent, OrderSide, OrderStatus, OrderType, ProtoEnum, TickType, TimeInForce

# Error types
from tektii.strategy.models.errors import (  # Exceptions
    ConfigurationError,
    ConnectionError,
    OrderRejectionError,
    OrderValidationError,
    RejectCode,
    StrategyError,
    SystemEventType,
    TektiiError,
    ValidationErrorCode,
    ValidationWarningCode,
)

# Event models
from tektii.strategy.models.events import AccountUpdateEvent, OrderUpdateEvent, PositionUpdateEvent, SystemEvent, TektiiEvent, TradeEvent

# Market data models
from tektii.strategy.models.market_data import BarData, OptionGreeks, TickData

# Order models
from tektii.strategy.models.orders import Order, OrderBuilder, ProtectiveOrdersOnFill, StopLimitOrder, StopOrder

# Risk models
from tektii.strategy.models.risk import PositionRisk, RiskCheckResult, ValidationError, ValidationWarning

# Service models
from tektii.strategy.models.service import (
    CancelOrderRequest,
    CancelOrderResponse,
    ClosePositionRequest,
    ClosePositionResponse,
    HistoricalDataRequest,
    HistoricalDataResponse,
    InitRequest,
    InitResponse,
    MarketDepthRequest,
    MarketDepthResponse,
    PlaceOrderRequest,
    PlaceOrderResponse,
    ProcessEventResponse,
    RiskMetricsRequest,
    RiskMetricsResponse,
    ShutdownRequest,
    ShutdownResponse,
    StateRequest,
    StateResponse,
    ValidateOrderRequest,
    ValidateOrderResponse,
)

__all__ = [
    # Common
    "Position",
    "AccountState",
    "Bar",
    "PriceLevel",
    # Enums
    "ProtoEnum",
    "OrderStatus",
    "OrderSide",
    "OrderType",
    "OrderIntent",
    "TimeInForce",
    "TickType",
    "BarType",
    # Error types
    "SystemEventType",
    "RejectCode",
    "ValidationErrorCode",
    "ValidationWarningCode",
    # Exceptions
    "TektiiError",
    "OrderValidationError",
    "OrderRejectionError",
    "StrategyError",
    "ConnectionError",
    "ConfigurationError",
    # Orders
    "Order",
    "StopOrder",
    "StopLimitOrder",
    "ProtectiveOrdersOnFill",
    "OrderBuilder",
    # Market Data
    "TickData",
    "BarData",
    "OptionGreeks",
    # Events
    "OrderUpdateEvent",
    "PositionUpdateEvent",
    "AccountUpdateEvent",
    "TradeEvent",
    "SystemEvent",
    "TektiiEvent",
    # Service
    "InitRequest",
    "InitResponse",
    "ShutdownRequest",
    "ShutdownResponse",
    "ProcessEventResponse",
    "StateRequest",
    "StateResponse",
    "HistoricalDataRequest",
    "HistoricalDataResponse",
    "MarketDepthRequest",
    "MarketDepthResponse",
    "RiskMetricsRequest",
    "RiskMetricsResponse",
    "PlaceOrderRequest",
    "PlaceOrderResponse",
    "CancelOrderRequest",
    "CancelOrderResponse",
    "ValidateOrderRequest",
    "ValidateOrderResponse",
    "ClosePositionRequest",
    "ClosePositionResponse",
    # Risk
    "RiskCheckResult",
    "ValidationError",
    "ValidationWarning",
    "PositionRisk",
]
