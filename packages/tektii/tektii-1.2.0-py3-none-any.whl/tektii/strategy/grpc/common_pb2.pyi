from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class OrderStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ORDER_STATUS_UNKNOWN: _ClassVar[OrderStatus]
    ORDER_STATUS_PENDING: _ClassVar[OrderStatus]
    ORDER_STATUS_SUBMITTED: _ClassVar[OrderStatus]
    ORDER_STATUS_ACCEPTED: _ClassVar[OrderStatus]
    ORDER_STATUS_PARTIAL: _ClassVar[OrderStatus]
    ORDER_STATUS_FILLED: _ClassVar[OrderStatus]
    ORDER_STATUS_CANCELED: _ClassVar[OrderStatus]
    ORDER_STATUS_REJECTED: _ClassVar[OrderStatus]
    ORDER_STATUS_EXPIRED: _ClassVar[OrderStatus]

class OrderSide(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ORDER_SIDE_UNKNOWN: _ClassVar[OrderSide]
    ORDER_SIDE_BUY: _ClassVar[OrderSide]
    ORDER_SIDE_SELL: _ClassVar[OrderSide]

class OrderType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ORDER_TYPE_UNKNOWN: _ClassVar[OrderType]
    ORDER_TYPE_MARKET: _ClassVar[OrderType]
    ORDER_TYPE_LIMIT: _ClassVar[OrderType]
    ORDER_TYPE_STOP: _ClassVar[OrderType]
    ORDER_TYPE_STOP_LIMIT: _ClassVar[OrderType]

class OrderIntent(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ORDER_INTENT_UNKNOWN: _ClassVar[OrderIntent]
    ORDER_INTENT_OPEN: _ClassVar[OrderIntent]
    ORDER_INTENT_CLOSE: _ClassVar[OrderIntent]
    ORDER_INTENT_STOP_LOSS: _ClassVar[OrderIntent]
    ORDER_INTENT_TAKE_PROFIT: _ClassVar[OrderIntent]

class TimeInForce(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TIME_IN_FORCE_UNKNOWN: _ClassVar[TimeInForce]
    TIME_IN_FORCE_DAY: _ClassVar[TimeInForce]
    TIME_IN_FORCE_GTC: _ClassVar[TimeInForce]
    TIME_IN_FORCE_IOC: _ClassVar[TimeInForce]
    TIME_IN_FORCE_FOK: _ClassVar[TimeInForce]

class SystemEventType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SYSTEM_EVENT_UNKNOWN: _ClassVar[SystemEventType]
    SYSTEM_EVENT_CONNECTED: _ClassVar[SystemEventType]
    SYSTEM_EVENT_DISCONNECTED: _ClassVar[SystemEventType]
    SYSTEM_EVENT_ERROR: _ClassVar[SystemEventType]
    SYSTEM_EVENT_WARNING: _ClassVar[SystemEventType]
    SYSTEM_EVENT_INFO: _ClassVar[SystemEventType]

class RejectCode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    REJECT_CODE_UNKNOWN: _ClassVar[RejectCode]
    REJECT_CODE_INSUFFICIENT_MARGIN: _ClassVar[RejectCode]
    REJECT_CODE_POSITION_LIMIT: _ClassVar[RejectCode]
    REJECT_CODE_INVALID_SYMBOL: _ClassVar[RejectCode]
    REJECT_CODE_MARKET_CLOSED: _ClassVar[RejectCode]
    REJECT_CODE_INVALID_QUANTITY: _ClassVar[RejectCode]
    REJECT_CODE_INVALID_PRICE: _ClassVar[RejectCode]
    REJECT_CODE_RATE_LIMIT: _ClassVar[RejectCode]
    REJECT_CODE_DUPLICATE_ORDER: _ClassVar[RejectCode]
    REJECT_CODE_ACCOUNT_RESTRICTED: _ClassVar[RejectCode]
    REJECT_CODE_ORDER_NOT_FOUND: _ClassVar[RejectCode]
    REJECT_CODE_ORDER_NOT_MODIFIABLE: _ClassVar[RejectCode]
    REJECT_CODE_RISK_CHECK_FAILED: _ClassVar[RejectCode]

class ValidationErrorCode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    VALIDATION_ERROR_UNKNOWN: _ClassVar[ValidationErrorCode]
    VALIDATION_ERROR_INVALID_SYMBOL: _ClassVar[ValidationErrorCode]
    VALIDATION_ERROR_INVALID_QUANTITY: _ClassVar[ValidationErrorCode]
    VALIDATION_ERROR_INVALID_PRICE: _ClassVar[ValidationErrorCode]
    VALIDATION_ERROR_MISSING_REQUIRED_FIELD: _ClassVar[ValidationErrorCode]
    VALIDATION_ERROR_CONFLICTING_FIELDS: _ClassVar[ValidationErrorCode]

class ValidationWarningCode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    VALIDATION_WARNING_UNKNOWN: _ClassVar[ValidationWarningCode]
    VALIDATION_WARNING_HIGH_CONCENTRATION: _ClassVar[ValidationWarningCode]
    VALIDATION_WARNING_UNUSUAL_SIZE: _ClassVar[ValidationWarningCode]
    VALIDATION_WARNING_FAR_FROM_MARKET: _ClassVar[ValidationWarningCode]
    VALIDATION_WARNING_LOW_LIQUIDITY: _ClassVar[ValidationWarningCode]
    VALIDATION_WARNING_HIGH_VOLATILITY: _ClassVar[ValidationWarningCode]
ORDER_STATUS_UNKNOWN: OrderStatus
ORDER_STATUS_PENDING: OrderStatus
ORDER_STATUS_SUBMITTED: OrderStatus
ORDER_STATUS_ACCEPTED: OrderStatus
ORDER_STATUS_PARTIAL: OrderStatus
ORDER_STATUS_FILLED: OrderStatus
ORDER_STATUS_CANCELED: OrderStatus
ORDER_STATUS_REJECTED: OrderStatus
ORDER_STATUS_EXPIRED: OrderStatus
ORDER_SIDE_UNKNOWN: OrderSide
ORDER_SIDE_BUY: OrderSide
ORDER_SIDE_SELL: OrderSide
ORDER_TYPE_UNKNOWN: OrderType
ORDER_TYPE_MARKET: OrderType
ORDER_TYPE_LIMIT: OrderType
ORDER_TYPE_STOP: OrderType
ORDER_TYPE_STOP_LIMIT: OrderType
ORDER_INTENT_UNKNOWN: OrderIntent
ORDER_INTENT_OPEN: OrderIntent
ORDER_INTENT_CLOSE: OrderIntent
ORDER_INTENT_STOP_LOSS: OrderIntent
ORDER_INTENT_TAKE_PROFIT: OrderIntent
TIME_IN_FORCE_UNKNOWN: TimeInForce
TIME_IN_FORCE_DAY: TimeInForce
TIME_IN_FORCE_GTC: TimeInForce
TIME_IN_FORCE_IOC: TimeInForce
TIME_IN_FORCE_FOK: TimeInForce
SYSTEM_EVENT_UNKNOWN: SystemEventType
SYSTEM_EVENT_CONNECTED: SystemEventType
SYSTEM_EVENT_DISCONNECTED: SystemEventType
SYSTEM_EVENT_ERROR: SystemEventType
SYSTEM_EVENT_WARNING: SystemEventType
SYSTEM_EVENT_INFO: SystemEventType
REJECT_CODE_UNKNOWN: RejectCode
REJECT_CODE_INSUFFICIENT_MARGIN: RejectCode
REJECT_CODE_POSITION_LIMIT: RejectCode
REJECT_CODE_INVALID_SYMBOL: RejectCode
REJECT_CODE_MARKET_CLOSED: RejectCode
REJECT_CODE_INVALID_QUANTITY: RejectCode
REJECT_CODE_INVALID_PRICE: RejectCode
REJECT_CODE_RATE_LIMIT: RejectCode
REJECT_CODE_DUPLICATE_ORDER: RejectCode
REJECT_CODE_ACCOUNT_RESTRICTED: RejectCode
REJECT_CODE_ORDER_NOT_FOUND: RejectCode
REJECT_CODE_ORDER_NOT_MODIFIABLE: RejectCode
REJECT_CODE_RISK_CHECK_FAILED: RejectCode
VALIDATION_ERROR_UNKNOWN: ValidationErrorCode
VALIDATION_ERROR_INVALID_SYMBOL: ValidationErrorCode
VALIDATION_ERROR_INVALID_QUANTITY: ValidationErrorCode
VALIDATION_ERROR_INVALID_PRICE: ValidationErrorCode
VALIDATION_ERROR_MISSING_REQUIRED_FIELD: ValidationErrorCode
VALIDATION_ERROR_CONFLICTING_FIELDS: ValidationErrorCode
VALIDATION_WARNING_UNKNOWN: ValidationWarningCode
VALIDATION_WARNING_HIGH_CONCENTRATION: ValidationWarningCode
VALIDATION_WARNING_UNUSUAL_SIZE: ValidationWarningCode
VALIDATION_WARNING_FAR_FROM_MARKET: ValidationWarningCode
VALIDATION_WARNING_LOW_LIQUIDITY: ValidationWarningCode
VALIDATION_WARNING_HIGH_VOLATILITY: ValidationWarningCode

class Position(_message.Message):
    __slots__ = ("symbol", "quantity", "avg_price", "market_value", "unrealized_pnl", "realized_pnl", "current_price")
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    AVG_PRICE_FIELD_NUMBER: _ClassVar[int]
    MARKET_VALUE_FIELD_NUMBER: _ClassVar[int]
    UNREALIZED_PNL_FIELD_NUMBER: _ClassVar[int]
    REALIZED_PNL_FIELD_NUMBER: _ClassVar[int]
    CURRENT_PRICE_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    quantity: float
    avg_price: float
    market_value: float
    unrealized_pnl: float
    realized_pnl: float
    current_price: float
    def __init__(self, symbol: _Optional[str] = ..., quantity: _Optional[float] = ..., avg_price: _Optional[float] = ..., market_value: _Optional[float] = ..., unrealized_pnl: _Optional[float] = ..., realized_pnl: _Optional[float] = ..., current_price: _Optional[float] = ...) -> None: ...

class Order(_message.Message):
    __slots__ = ("order_id", "symbol", "status", "side", "order_type", "quantity", "filled_quantity", "limit_price", "stop_price", "created_at_us", "order_intent", "parent_trade_id")
    ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SIDE_FIELD_NUMBER: _ClassVar[int]
    ORDER_TYPE_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    FILLED_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    LIMIT_PRICE_FIELD_NUMBER: _ClassVar[int]
    STOP_PRICE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_US_FIELD_NUMBER: _ClassVar[int]
    ORDER_INTENT_FIELD_NUMBER: _ClassVar[int]
    PARENT_TRADE_ID_FIELD_NUMBER: _ClassVar[int]
    order_id: str
    symbol: str
    status: OrderStatus
    side: OrderSide
    order_type: OrderType
    quantity: float
    filled_quantity: float
    limit_price: float
    stop_price: float
    created_at_us: int
    order_intent: OrderIntent
    parent_trade_id: str
    def __init__(self, order_id: _Optional[str] = ..., symbol: _Optional[str] = ..., status: _Optional[_Union[OrderStatus, str]] = ..., side: _Optional[_Union[OrderSide, str]] = ..., order_type: _Optional[_Union[OrderType, str]] = ..., quantity: _Optional[float] = ..., filled_quantity: _Optional[float] = ..., limit_price: _Optional[float] = ..., stop_price: _Optional[float] = ..., created_at_us: _Optional[int] = ..., order_intent: _Optional[_Union[OrderIntent, str]] = ..., parent_trade_id: _Optional[str] = ...) -> None: ...

class AccountState(_message.Message):
    __slots__ = ("cash_balance", "portfolio_value", "buying_power", "initial_margin", "maintenance_margin", "margin_used", "daily_pnl", "total_pnl")
    CASH_BALANCE_FIELD_NUMBER: _ClassVar[int]
    PORTFOLIO_VALUE_FIELD_NUMBER: _ClassVar[int]
    BUYING_POWER_FIELD_NUMBER: _ClassVar[int]
    INITIAL_MARGIN_FIELD_NUMBER: _ClassVar[int]
    MAINTENANCE_MARGIN_FIELD_NUMBER: _ClassVar[int]
    MARGIN_USED_FIELD_NUMBER: _ClassVar[int]
    DAILY_PNL_FIELD_NUMBER: _ClassVar[int]
    TOTAL_PNL_FIELD_NUMBER: _ClassVar[int]
    cash_balance: float
    portfolio_value: float
    buying_power: float
    initial_margin: float
    maintenance_margin: float
    margin_used: float
    daily_pnl: float
    total_pnl: float
    def __init__(self, cash_balance: _Optional[float] = ..., portfolio_value: _Optional[float] = ..., buying_power: _Optional[float] = ..., initial_margin: _Optional[float] = ..., maintenance_margin: _Optional[float] = ..., margin_used: _Optional[float] = ..., daily_pnl: _Optional[float] = ..., total_pnl: _Optional[float] = ...) -> None: ...

class Bar(_message.Message):
    __slots__ = ("timestamp_us", "open", "high", "low", "close", "volume", "vwap")
    TIMESTAMP_US_FIELD_NUMBER: _ClassVar[int]
    OPEN_FIELD_NUMBER: _ClassVar[int]
    HIGH_FIELD_NUMBER: _ClassVar[int]
    LOW_FIELD_NUMBER: _ClassVar[int]
    CLOSE_FIELD_NUMBER: _ClassVar[int]
    VOLUME_FIELD_NUMBER: _ClassVar[int]
    VWAP_FIELD_NUMBER: _ClassVar[int]
    timestamp_us: int
    open: float
    high: float
    low: float
    close: float
    volume: int
    vwap: float
    def __init__(self, timestamp_us: _Optional[int] = ..., open: _Optional[float] = ..., high: _Optional[float] = ..., low: _Optional[float] = ..., close: _Optional[float] = ..., volume: _Optional[int] = ..., vwap: _Optional[float] = ...) -> None: ...

class PriceLevel(_message.Message):
    __slots__ = ("price", "size", "order_count")
    PRICE_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    ORDER_COUNT_FIELD_NUMBER: _ClassVar[int]
    price: float
    size: float
    order_count: int
    def __init__(self, price: _Optional[float] = ..., size: _Optional[float] = ..., order_count: _Optional[int] = ...) -> None: ...

class ValidationError(_message.Message):
    __slots__ = ("field", "message", "code")
    FIELD_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    field: str
    message: str
    code: ValidationErrorCode
    def __init__(self, field: _Optional[str] = ..., message: _Optional[str] = ..., code: _Optional[_Union[ValidationErrorCode, str]] = ...) -> None: ...

class ValidationWarning(_message.Message):
    __slots__ = ("field", "message", "code")
    FIELD_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    field: str
    message: str
    code: ValidationWarningCode
    def __init__(self, field: _Optional[str] = ..., message: _Optional[str] = ..., code: _Optional[_Union[ValidationWarningCode, str]] = ...) -> None: ...

class RiskCheckResult(_message.Message):
    __slots__ = ("margin_required", "margin_available", "buying_power_used", "buying_power_remaining", "position_limit", "current_position", "resulting_position", "portfolio_var_before", "portfolio_var_after", "concentration_risk", "warnings")
    class WarningsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    MARGIN_REQUIRED_FIELD_NUMBER: _ClassVar[int]
    MARGIN_AVAILABLE_FIELD_NUMBER: _ClassVar[int]
    BUYING_POWER_USED_FIELD_NUMBER: _ClassVar[int]
    BUYING_POWER_REMAINING_FIELD_NUMBER: _ClassVar[int]
    POSITION_LIMIT_FIELD_NUMBER: _ClassVar[int]
    CURRENT_POSITION_FIELD_NUMBER: _ClassVar[int]
    RESULTING_POSITION_FIELD_NUMBER: _ClassVar[int]
    PORTFOLIO_VAR_BEFORE_FIELD_NUMBER: _ClassVar[int]
    PORTFOLIO_VAR_AFTER_FIELD_NUMBER: _ClassVar[int]
    CONCENTRATION_RISK_FIELD_NUMBER: _ClassVar[int]
    WARNINGS_FIELD_NUMBER: _ClassVar[int]
    margin_required: float
    margin_available: float
    buying_power_used: float
    buying_power_remaining: float
    position_limit: float
    current_position: float
    resulting_position: float
    portfolio_var_before: float
    portfolio_var_after: float
    concentration_risk: float
    warnings: _containers.ScalarMap[str, str]
    def __init__(self, margin_required: _Optional[float] = ..., margin_available: _Optional[float] = ..., buying_power_used: _Optional[float] = ..., buying_power_remaining: _Optional[float] = ..., position_limit: _Optional[float] = ..., current_position: _Optional[float] = ..., resulting_position: _Optional[float] = ..., portfolio_var_before: _Optional[float] = ..., portfolio_var_after: _Optional[float] = ..., concentration_risk: _Optional[float] = ..., warnings: _Optional[_Mapping[str, str]] = ...) -> None: ...

class StopOrder(_message.Message):
    __slots__ = ("stop_price",)
    STOP_PRICE_FIELD_NUMBER: _ClassVar[int]
    stop_price: float
    def __init__(self, stop_price: _Optional[float] = ...) -> None: ...

class StopLimitOrder(_message.Message):
    __slots__ = ("stop_price", "limit_price")
    STOP_PRICE_FIELD_NUMBER: _ClassVar[int]
    LIMIT_PRICE_FIELD_NUMBER: _ClassVar[int]
    stop_price: float
    limit_price: float
    def __init__(self, stop_price: _Optional[float] = ..., limit_price: _Optional[float] = ...) -> None: ...

class ProtectiveOrdersOnFill(_message.Message):
    __slots__ = ("stop", "stop_limit", "take_profit_price")
    STOP_FIELD_NUMBER: _ClassVar[int]
    STOP_LIMIT_FIELD_NUMBER: _ClassVar[int]
    TAKE_PROFIT_PRICE_FIELD_NUMBER: _ClassVar[int]
    stop: StopOrder
    stop_limit: StopLimitOrder
    take_profit_price: float
    def __init__(self, stop: _Optional[_Union[StopOrder, _Mapping]] = ..., stop_limit: _Optional[_Union[StopLimitOrder, _Mapping]] = ..., take_profit_price: _Optional[float] = ...) -> None: ...

class PositionRisk(_message.Message):
    __slots__ = ("symbol", "position_var", "beta", "volatility", "exposure")
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    POSITION_VAR_FIELD_NUMBER: _ClassVar[int]
    BETA_FIELD_NUMBER: _ClassVar[int]
    VOLATILITY_FIELD_NUMBER: _ClassVar[int]
    EXPOSURE_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    position_var: float
    beta: float
    volatility: float
    exposure: float
    def __init__(self, symbol: _Optional[str] = ..., position_var: _Optional[float] = ..., beta: _Optional[float] = ..., volatility: _Optional[float] = ..., exposure: _Optional[float] = ...) -> None: ...
