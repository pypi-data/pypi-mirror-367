from google.protobuf import wrappers_pb2 as _wrappers_pb2
from trading.v1 import common_pb2 as _common_pb2
from trading.v1 import market_data_pb2 as _market_data_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TektiiEvent(_message.Message):
    __slots__ = ("event_id", "timestamp_us", "tick_data", "bar_data", "option_greeks", "order_update", "position_update", "account_update", "trade", "system")
    EVENT_ID_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_US_FIELD_NUMBER: _ClassVar[int]
    TICK_DATA_FIELD_NUMBER: _ClassVar[int]
    BAR_DATA_FIELD_NUMBER: _ClassVar[int]
    OPTION_GREEKS_FIELD_NUMBER: _ClassVar[int]
    ORDER_UPDATE_FIELD_NUMBER: _ClassVar[int]
    POSITION_UPDATE_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_UPDATE_FIELD_NUMBER: _ClassVar[int]
    TRADE_FIELD_NUMBER: _ClassVar[int]
    SYSTEM_FIELD_NUMBER: _ClassVar[int]
    event_id: str
    timestamp_us: int
    tick_data: _market_data_pb2.TickData
    bar_data: _market_data_pb2.BarData
    option_greeks: _market_data_pb2.OptionGreeks
    order_update: _market_data_pb2.OrderUpdateEvent
    position_update: _market_data_pb2.PositionUpdateEvent
    account_update: _market_data_pb2.AccountUpdateEvent
    trade: _market_data_pb2.TradeEvent
    system: _market_data_pb2.SystemEvent
    def __init__(self, event_id: _Optional[str] = ..., timestamp_us: _Optional[int] = ..., tick_data: _Optional[_Union[_market_data_pb2.TickData, _Mapping]] = ..., bar_data: _Optional[_Union[_market_data_pb2.BarData, _Mapping]] = ..., option_greeks: _Optional[_Union[_market_data_pb2.OptionGreeks, _Mapping]] = ..., order_update: _Optional[_Union[_market_data_pb2.OrderUpdateEvent, _Mapping]] = ..., position_update: _Optional[_Union[_market_data_pb2.PositionUpdateEvent, _Mapping]] = ..., account_update: _Optional[_Union[_market_data_pb2.AccountUpdateEvent, _Mapping]] = ..., trade: _Optional[_Union[_market_data_pb2.TradeEvent, _Mapping]] = ..., system: _Optional[_Union[_market_data_pb2.SystemEvent, _Mapping]] = ...) -> None: ...

class ProcessEventResponse(_message.Message):
    __slots__ = ("success", "error", "metadata")
    class MetadataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: str
    metadata: _containers.ScalarMap[str, str]
    def __init__(self, success: bool = ..., error: _Optional[str] = ..., metadata: _Optional[_Mapping[str, str]] = ...) -> None: ...

class InitRequest(_message.Message):
    __slots__ = ("config", "symbols", "strategy_id")
    class ConfigEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    SYMBOLS_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_ID_FIELD_NUMBER: _ClassVar[int]
    config: _containers.ScalarMap[str, str]
    symbols: _containers.RepeatedScalarFieldContainer[str]
    strategy_id: str
    def __init__(self, config: _Optional[_Mapping[str, str]] = ..., symbols: _Optional[_Iterable[str]] = ..., strategy_id: _Optional[str] = ...) -> None: ...

class InitResponse(_message.Message):
    __slots__ = ("success", "message", "capabilities")
    class CapabilitiesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    CAPABILITIES_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    capabilities: _containers.ScalarMap[str, str]
    def __init__(self, success: bool = ..., message: _Optional[str] = ..., capabilities: _Optional[_Mapping[str, str]] = ...) -> None: ...

class ShutdownRequest(_message.Message):
    __slots__ = ("reason", "force")
    REASON_FIELD_NUMBER: _ClassVar[int]
    FORCE_FIELD_NUMBER: _ClassVar[int]
    reason: str
    force: bool
    def __init__(self, reason: _Optional[str] = ..., force: bool = ...) -> None: ...

class ShutdownResponse(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ...) -> None: ...

class StateRequest(_message.Message):
    __slots__ = ("symbols", "include_positions", "include_orders", "include_account")
    SYMBOLS_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_POSITIONS_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_ORDERS_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_ACCOUNT_FIELD_NUMBER: _ClassVar[int]
    symbols: _containers.RepeatedScalarFieldContainer[str]
    include_positions: bool
    include_orders: bool
    include_account: bool
    def __init__(self, symbols: _Optional[_Iterable[str]] = ..., include_positions: bool = ..., include_orders: bool = ..., include_account: bool = ...) -> None: ...

class StateResponse(_message.Message):
    __slots__ = ("positions", "orders", "account", "timestamp_us")
    class PositionsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _common_pb2.Position
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_common_pb2.Position, _Mapping]] = ...) -> None: ...
    class OrdersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _common_pb2.Order
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_common_pb2.Order, _Mapping]] = ...) -> None: ...
    POSITIONS_FIELD_NUMBER: _ClassVar[int]
    ORDERS_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_US_FIELD_NUMBER: _ClassVar[int]
    positions: _containers.MessageMap[str, _common_pb2.Position]
    orders: _containers.MessageMap[str, _common_pb2.Order]
    account: _common_pb2.AccountState
    timestamp_us: int
    def __init__(self, positions: _Optional[_Mapping[str, _common_pb2.Position]] = ..., orders: _Optional[_Mapping[str, _common_pb2.Order]] = ..., account: _Optional[_Union[_common_pb2.AccountState, _Mapping]] = ..., timestamp_us: _Optional[int] = ...) -> None: ...

class RiskMetricsRequest(_message.Message):
    __slots__ = ("symbols", "confidence_level", "lookback_days")
    SYMBOLS_FIELD_NUMBER: _ClassVar[int]
    CONFIDENCE_LEVEL_FIELD_NUMBER: _ClassVar[int]
    LOOKBACK_DAYS_FIELD_NUMBER: _ClassVar[int]
    symbols: _containers.RepeatedScalarFieldContainer[str]
    confidence_level: float
    lookback_days: int
    def __init__(self, symbols: _Optional[_Iterable[str]] = ..., confidence_level: _Optional[float] = ..., lookback_days: _Optional[int] = ...) -> None: ...

class RiskMetricsResponse(_message.Message):
    __slots__ = ("portfolio_var", "portfolio_sharpe", "portfolio_beta", "max_drawdown", "position_risks", "correlations", "timestamp_us")
    class PositionRisksEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _common_pb2.PositionRisk
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_common_pb2.PositionRisk, _Mapping]] = ...) -> None: ...
    class CorrelationsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: float
        def __init__(self, key: _Optional[str] = ..., value: _Optional[float] = ...) -> None: ...
    PORTFOLIO_VAR_FIELD_NUMBER: _ClassVar[int]
    PORTFOLIO_SHARPE_FIELD_NUMBER: _ClassVar[int]
    PORTFOLIO_BETA_FIELD_NUMBER: _ClassVar[int]
    MAX_DRAWDOWN_FIELD_NUMBER: _ClassVar[int]
    POSITION_RISKS_FIELD_NUMBER: _ClassVar[int]
    CORRELATIONS_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_US_FIELD_NUMBER: _ClassVar[int]
    portfolio_var: float
    portfolio_sharpe: float
    portfolio_beta: float
    max_drawdown: float
    position_risks: _containers.MessageMap[str, _common_pb2.PositionRisk]
    correlations: _containers.ScalarMap[str, float]
    timestamp_us: int
    def __init__(self, portfolio_var: _Optional[float] = ..., portfolio_sharpe: _Optional[float] = ..., portfolio_beta: _Optional[float] = ..., max_drawdown: _Optional[float] = ..., position_risks: _Optional[_Mapping[str, _common_pb2.PositionRisk]] = ..., correlations: _Optional[_Mapping[str, float]] = ..., timestamp_us: _Optional[int] = ...) -> None: ...

class PlaceOrderRequest(_message.Message):
    __slots__ = ("symbol", "side", "order_type", "quantity", "limit_price", "stop_price", "time_in_force", "client_order_id", "metadata", "order_intent", "parent_trade_id", "protective_orders_on_fill", "request_id", "validate_only")
    class MetadataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    SIDE_FIELD_NUMBER: _ClassVar[int]
    ORDER_TYPE_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    LIMIT_PRICE_FIELD_NUMBER: _ClassVar[int]
    STOP_PRICE_FIELD_NUMBER: _ClassVar[int]
    TIME_IN_FORCE_FIELD_NUMBER: _ClassVar[int]
    CLIENT_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    ORDER_INTENT_FIELD_NUMBER: _ClassVar[int]
    PARENT_TRADE_ID_FIELD_NUMBER: _ClassVar[int]
    PROTECTIVE_ORDERS_ON_FILL_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    VALIDATE_ONLY_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    side: _common_pb2.OrderSide
    order_type: _common_pb2.OrderType
    quantity: float
    limit_price: float
    stop_price: float
    time_in_force: _common_pb2.TimeInForce
    client_order_id: str
    metadata: _containers.ScalarMap[str, str]
    order_intent: _common_pb2.OrderIntent
    parent_trade_id: str
    protective_orders_on_fill: _common_pb2.ProtectiveOrdersOnFill
    request_id: str
    validate_only: bool
    def __init__(self, symbol: _Optional[str] = ..., side: _Optional[_Union[_common_pb2.OrderSide, str]] = ..., order_type: _Optional[_Union[_common_pb2.OrderType, str]] = ..., quantity: _Optional[float] = ..., limit_price: _Optional[float] = ..., stop_price: _Optional[float] = ..., time_in_force: _Optional[_Union[_common_pb2.TimeInForce, str]] = ..., client_order_id: _Optional[str] = ..., metadata: _Optional[_Mapping[str, str]] = ..., order_intent: _Optional[_Union[_common_pb2.OrderIntent, str]] = ..., parent_trade_id: _Optional[str] = ..., protective_orders_on_fill: _Optional[_Union[_common_pb2.ProtectiveOrdersOnFill, _Mapping]] = ..., request_id: _Optional[str] = ..., validate_only: bool = ...) -> None: ...

class PlaceOrderResponse(_message.Message):
    __slots__ = ("accepted", "order_id", "request_id", "reject_reason", "reject_code", "risk_check", "estimated_fill_price", "estimated_commission", "timestamp_us")
    ACCEPTED_FIELD_NUMBER: _ClassVar[int]
    ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    REJECT_REASON_FIELD_NUMBER: _ClassVar[int]
    REJECT_CODE_FIELD_NUMBER: _ClassVar[int]
    RISK_CHECK_FIELD_NUMBER: _ClassVar[int]
    ESTIMATED_FILL_PRICE_FIELD_NUMBER: _ClassVar[int]
    ESTIMATED_COMMISSION_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_US_FIELD_NUMBER: _ClassVar[int]
    accepted: bool
    order_id: str
    request_id: str
    reject_reason: str
    reject_code: _common_pb2.RejectCode
    risk_check: _common_pb2.RiskCheckResult
    estimated_fill_price: float
    estimated_commission: float
    timestamp_us: int
    def __init__(self, accepted: bool = ..., order_id: _Optional[str] = ..., request_id: _Optional[str] = ..., reject_reason: _Optional[str] = ..., reject_code: _Optional[_Union[_common_pb2.RejectCode, str]] = ..., risk_check: _Optional[_Union[_common_pb2.RiskCheckResult, _Mapping]] = ..., estimated_fill_price: _Optional[float] = ..., estimated_commission: _Optional[float] = ..., timestamp_us: _Optional[int] = ...) -> None: ...

class CancelOrderRequest(_message.Message):
    __slots__ = ("order_id", "request_id")
    ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    order_id: str
    request_id: str
    def __init__(self, order_id: _Optional[str] = ..., request_id: _Optional[str] = ...) -> None: ...

class CancelOrderResponse(_message.Message):
    __slots__ = ("accepted", "order_id", "request_id", "reject_reason", "reject_code", "previous_status", "filled_quantity", "timestamp_us")
    ACCEPTED_FIELD_NUMBER: _ClassVar[int]
    ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    REJECT_REASON_FIELD_NUMBER: _ClassVar[int]
    REJECT_CODE_FIELD_NUMBER: _ClassVar[int]
    PREVIOUS_STATUS_FIELD_NUMBER: _ClassVar[int]
    FILLED_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_US_FIELD_NUMBER: _ClassVar[int]
    accepted: bool
    order_id: str
    request_id: str
    reject_reason: str
    reject_code: _common_pb2.RejectCode
    previous_status: _common_pb2.OrderStatus
    filled_quantity: float
    timestamp_us: int
    def __init__(self, accepted: bool = ..., order_id: _Optional[str] = ..., request_id: _Optional[str] = ..., reject_reason: _Optional[str] = ..., reject_code: _Optional[_Union[_common_pb2.RejectCode, str]] = ..., previous_status: _Optional[_Union[_common_pb2.OrderStatus, str]] = ..., filled_quantity: _Optional[float] = ..., timestamp_us: _Optional[int] = ...) -> None: ...

class ModifyOrderRequest(_message.Message):
    __slots__ = ("order_id", "quantity", "limit_price", "stop_price", "request_id")
    ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    LIMIT_PRICE_FIELD_NUMBER: _ClassVar[int]
    STOP_PRICE_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    order_id: str
    quantity: _wrappers_pb2.DoubleValue
    limit_price: _wrappers_pb2.DoubleValue
    stop_price: _wrappers_pb2.DoubleValue
    request_id: str
    def __init__(self, order_id: _Optional[str] = ..., quantity: _Optional[_Union[_wrappers_pb2.DoubleValue, _Mapping]] = ..., limit_price: _Optional[_Union[_wrappers_pb2.DoubleValue, _Mapping]] = ..., stop_price: _Optional[_Union[_wrappers_pb2.DoubleValue, _Mapping]] = ..., request_id: _Optional[str] = ...) -> None: ...

class ModifyOrderResponse(_message.Message):
    __slots__ = ("accepted", "order_id", "request_id", "reject_reason", "reject_code", "risk_check", "timestamp_us")
    ACCEPTED_FIELD_NUMBER: _ClassVar[int]
    ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    REJECT_REASON_FIELD_NUMBER: _ClassVar[int]
    REJECT_CODE_FIELD_NUMBER: _ClassVar[int]
    RISK_CHECK_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_US_FIELD_NUMBER: _ClassVar[int]
    accepted: bool
    order_id: str
    request_id: str
    reject_reason: str
    reject_code: _common_pb2.RejectCode
    risk_check: _common_pb2.RiskCheckResult
    timestamp_us: int
    def __init__(self, accepted: bool = ..., order_id: _Optional[str] = ..., request_id: _Optional[str] = ..., reject_reason: _Optional[str] = ..., reject_code: _Optional[_Union[_common_pb2.RejectCode, str]] = ..., risk_check: _Optional[_Union[_common_pb2.RiskCheckResult, _Mapping]] = ..., timestamp_us: _Optional[int] = ...) -> None: ...

class ValidateOrderRequest(_message.Message):
    __slots__ = ("symbol", "side", "order_type", "quantity", "limit_price", "stop_price", "request_id")
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    SIDE_FIELD_NUMBER: _ClassVar[int]
    ORDER_TYPE_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    LIMIT_PRICE_FIELD_NUMBER: _ClassVar[int]
    STOP_PRICE_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    side: _common_pb2.OrderSide
    order_type: _common_pb2.OrderType
    quantity: float
    limit_price: float
    stop_price: float
    request_id: str
    def __init__(self, symbol: _Optional[str] = ..., side: _Optional[_Union[_common_pb2.OrderSide, str]] = ..., order_type: _Optional[_Union[_common_pb2.OrderType, str]] = ..., quantity: _Optional[float] = ..., limit_price: _Optional[float] = ..., stop_price: _Optional[float] = ..., request_id: _Optional[str] = ...) -> None: ...

class ValidateOrderResponse(_message.Message):
    __slots__ = ("valid", "request_id", "errors", "warnings", "risk_check", "estimated_fill_price", "estimated_market_impact")
    VALID_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    ERRORS_FIELD_NUMBER: _ClassVar[int]
    WARNINGS_FIELD_NUMBER: _ClassVar[int]
    RISK_CHECK_FIELD_NUMBER: _ClassVar[int]
    ESTIMATED_FILL_PRICE_FIELD_NUMBER: _ClassVar[int]
    ESTIMATED_MARKET_IMPACT_FIELD_NUMBER: _ClassVar[int]
    valid: bool
    request_id: str
    errors: _containers.RepeatedCompositeFieldContainer[_common_pb2.ValidationError]
    warnings: _containers.RepeatedCompositeFieldContainer[_common_pb2.ValidationWarning]
    risk_check: _common_pb2.RiskCheckResult
    estimated_fill_price: float
    estimated_market_impact: float
    def __init__(self, valid: bool = ..., request_id: _Optional[str] = ..., errors: _Optional[_Iterable[_Union[_common_pb2.ValidationError, _Mapping]]] = ..., warnings: _Optional[_Iterable[_Union[_common_pb2.ValidationWarning, _Mapping]]] = ..., risk_check: _Optional[_Union[_common_pb2.RiskCheckResult, _Mapping]] = ..., estimated_fill_price: _Optional[float] = ..., estimated_market_impact: _Optional[float] = ...) -> None: ...

class ClosePositionRequest(_message.Message):
    __slots__ = ("symbol", "quantity", "order_type", "limit_price", "request_id")
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    ORDER_TYPE_FIELD_NUMBER: _ClassVar[int]
    LIMIT_PRICE_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    quantity: float
    order_type: _common_pb2.OrderType
    limit_price: float
    request_id: str
    def __init__(self, symbol: _Optional[str] = ..., quantity: _Optional[float] = ..., order_type: _Optional[_Union[_common_pb2.OrderType, str]] = ..., limit_price: _Optional[float] = ..., request_id: _Optional[str] = ...) -> None: ...

class ClosePositionResponse(_message.Message):
    __slots__ = ("accepted", "request_id", "order_ids", "position_quantity", "closing_quantity", "remaining_quantity", "reject_reason", "reject_code", "timestamp_us")
    ACCEPTED_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    ORDER_IDS_FIELD_NUMBER: _ClassVar[int]
    POSITION_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    CLOSING_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    REMAINING_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    REJECT_REASON_FIELD_NUMBER: _ClassVar[int]
    REJECT_CODE_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_US_FIELD_NUMBER: _ClassVar[int]
    accepted: bool
    request_id: str
    order_ids: _containers.RepeatedScalarFieldContainer[str]
    position_quantity: float
    closing_quantity: float
    remaining_quantity: float
    reject_reason: str
    reject_code: _common_pb2.RejectCode
    timestamp_us: int
    def __init__(self, accepted: bool = ..., request_id: _Optional[str] = ..., order_ids: _Optional[_Iterable[str]] = ..., position_quantity: _Optional[float] = ..., closing_quantity: _Optional[float] = ..., remaining_quantity: _Optional[float] = ..., reject_reason: _Optional[str] = ..., reject_code: _Optional[_Union[_common_pb2.RejectCode, str]] = ..., timestamp_us: _Optional[int] = ...) -> None: ...

class ModifyTradeProtectionRequest(_message.Message):
    __slots__ = ("trade_id", "stop_loss", "take_profit", "request_id")
    class StopLossModification(_message.Message):
        __slots__ = ("stop", "stop_limit", "remove")
        STOP_FIELD_NUMBER: _ClassVar[int]
        STOP_LIMIT_FIELD_NUMBER: _ClassVar[int]
        REMOVE_FIELD_NUMBER: _ClassVar[int]
        stop: _common_pb2.StopOrder
        stop_limit: _common_pb2.StopLimitOrder
        remove: bool
        def __init__(self, stop: _Optional[_Union[_common_pb2.StopOrder, _Mapping]] = ..., stop_limit: _Optional[_Union[_common_pb2.StopLimitOrder, _Mapping]] = ..., remove: bool = ...) -> None: ...
    class TakeProfitModification(_message.Message):
        __slots__ = ("limit_price", "remove")
        LIMIT_PRICE_FIELD_NUMBER: _ClassVar[int]
        REMOVE_FIELD_NUMBER: _ClassVar[int]
        limit_price: float
        remove: bool
        def __init__(self, limit_price: _Optional[float] = ..., remove: bool = ...) -> None: ...
    TRADE_ID_FIELD_NUMBER: _ClassVar[int]
    STOP_LOSS_FIELD_NUMBER: _ClassVar[int]
    TAKE_PROFIT_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    trade_id: str
    stop_loss: ModifyTradeProtectionRequest.StopLossModification
    take_profit: ModifyTradeProtectionRequest.TakeProfitModification
    request_id: str
    def __init__(self, trade_id: _Optional[str] = ..., stop_loss: _Optional[_Union[ModifyTradeProtectionRequest.StopLossModification, _Mapping]] = ..., take_profit: _Optional[_Union[ModifyTradeProtectionRequest.TakeProfitModification, _Mapping]] = ..., request_id: _Optional[str] = ...) -> None: ...

class ModifyTradeProtectionResponse(_message.Message):
    __slots__ = ("accepted", "trade_id", "request_id", "stop_loss_order_id", "take_profit_order_id", "trade_quantity", "trade_entry_price", "current_price", "max_loss", "max_profit", "reject_reason", "reject_code", "timestamp_us")
    ACCEPTED_FIELD_NUMBER: _ClassVar[int]
    TRADE_ID_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    STOP_LOSS_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    TAKE_PROFIT_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    TRADE_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    TRADE_ENTRY_PRICE_FIELD_NUMBER: _ClassVar[int]
    CURRENT_PRICE_FIELD_NUMBER: _ClassVar[int]
    MAX_LOSS_FIELD_NUMBER: _ClassVar[int]
    MAX_PROFIT_FIELD_NUMBER: _ClassVar[int]
    REJECT_REASON_FIELD_NUMBER: _ClassVar[int]
    REJECT_CODE_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_US_FIELD_NUMBER: _ClassVar[int]
    accepted: bool
    trade_id: str
    request_id: str
    stop_loss_order_id: str
    take_profit_order_id: str
    trade_quantity: float
    trade_entry_price: float
    current_price: float
    max_loss: float
    max_profit: float
    reject_reason: str
    reject_code: _common_pb2.RejectCode
    timestamp_us: int
    def __init__(self, accepted: bool = ..., trade_id: _Optional[str] = ..., request_id: _Optional[str] = ..., stop_loss_order_id: _Optional[str] = ..., take_profit_order_id: _Optional[str] = ..., trade_quantity: _Optional[float] = ..., trade_entry_price: _Optional[float] = ..., current_price: _Optional[float] = ..., max_loss: _Optional[float] = ..., max_profit: _Optional[float] = ..., reject_reason: _Optional[str] = ..., reject_code: _Optional[_Union[_common_pb2.RejectCode, str]] = ..., timestamp_us: _Optional[int] = ...) -> None: ...
