from trading.v1 import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TickData(_message.Message):
    __slots__ = ("symbol", "bid", "ask", "bid_size", "ask_size", "last", "last_size", "mid", "exchange", "tick_type")
    class TickType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TICK_TYPE_UNKNOWN: _ClassVar[TickData.TickType]
        TICK_TYPE_QUOTE: _ClassVar[TickData.TickType]
        TICK_TYPE_TRADE: _ClassVar[TickData.TickType]
        TICK_TYPE_QUOTE_AND_TRADE: _ClassVar[TickData.TickType]
    TICK_TYPE_UNKNOWN: TickData.TickType
    TICK_TYPE_QUOTE: TickData.TickType
    TICK_TYPE_TRADE: TickData.TickType
    TICK_TYPE_QUOTE_AND_TRADE: TickData.TickType
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    BID_FIELD_NUMBER: _ClassVar[int]
    ASK_FIELD_NUMBER: _ClassVar[int]
    BID_SIZE_FIELD_NUMBER: _ClassVar[int]
    ASK_SIZE_FIELD_NUMBER: _ClassVar[int]
    LAST_FIELD_NUMBER: _ClassVar[int]
    LAST_SIZE_FIELD_NUMBER: _ClassVar[int]
    MID_FIELD_NUMBER: _ClassVar[int]
    EXCHANGE_FIELD_NUMBER: _ClassVar[int]
    TICK_TYPE_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    bid: float
    ask: float
    bid_size: int
    ask_size: int
    last: float
    last_size: int
    mid: float
    exchange: str
    tick_type: TickData.TickType
    def __init__(self, symbol: _Optional[str] = ..., bid: _Optional[float] = ..., ask: _Optional[float] = ..., bid_size: _Optional[int] = ..., ask_size: _Optional[int] = ..., last: _Optional[float] = ..., last_size: _Optional[int] = ..., mid: _Optional[float] = ..., exchange: _Optional[str] = ..., tick_type: _Optional[_Union[TickData.TickType, str]] = ...) -> None: ...

class BarData(_message.Message):
    __slots__ = ("symbol", "open", "high", "low", "close", "volume", "vwap", "trade_count", "bar_type", "bar_size", "bar_size_unit")
    class BarType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        BAR_TYPE_UNKNOWN: _ClassVar[BarData.BarType]
        BAR_TYPE_TIME: _ClassVar[BarData.BarType]
        BAR_TYPE_TICK: _ClassVar[BarData.BarType]
        BAR_TYPE_VOLUME: _ClassVar[BarData.BarType]
        BAR_TYPE_DOLLAR: _ClassVar[BarData.BarType]
    BAR_TYPE_UNKNOWN: BarData.BarType
    BAR_TYPE_TIME: BarData.BarType
    BAR_TYPE_TICK: BarData.BarType
    BAR_TYPE_VOLUME: BarData.BarType
    BAR_TYPE_DOLLAR: BarData.BarType
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    OPEN_FIELD_NUMBER: _ClassVar[int]
    HIGH_FIELD_NUMBER: _ClassVar[int]
    LOW_FIELD_NUMBER: _ClassVar[int]
    CLOSE_FIELD_NUMBER: _ClassVar[int]
    VOLUME_FIELD_NUMBER: _ClassVar[int]
    VWAP_FIELD_NUMBER: _ClassVar[int]
    TRADE_COUNT_FIELD_NUMBER: _ClassVar[int]
    BAR_TYPE_FIELD_NUMBER: _ClassVar[int]
    BAR_SIZE_FIELD_NUMBER: _ClassVar[int]
    BAR_SIZE_UNIT_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    vwap: float
    trade_count: int
    bar_type: BarData.BarType
    bar_size: int
    bar_size_unit: str
    def __init__(self, symbol: _Optional[str] = ..., open: _Optional[float] = ..., high: _Optional[float] = ..., low: _Optional[float] = ..., close: _Optional[float] = ..., volume: _Optional[int] = ..., vwap: _Optional[float] = ..., trade_count: _Optional[int] = ..., bar_type: _Optional[_Union[BarData.BarType, str]] = ..., bar_size: _Optional[int] = ..., bar_size_unit: _Optional[str] = ...) -> None: ...

class OptionGreeks(_message.Message):
    __slots__ = ("symbol", "delta", "gamma", "theta", "vega", "rho", "implied_volatility", "theoretical_value", "underlying_price", "interest_rate", "days_to_expiry")
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    DELTA_FIELD_NUMBER: _ClassVar[int]
    GAMMA_FIELD_NUMBER: _ClassVar[int]
    THETA_FIELD_NUMBER: _ClassVar[int]
    VEGA_FIELD_NUMBER: _ClassVar[int]
    RHO_FIELD_NUMBER: _ClassVar[int]
    IMPLIED_VOLATILITY_FIELD_NUMBER: _ClassVar[int]
    THEORETICAL_VALUE_FIELD_NUMBER: _ClassVar[int]
    UNDERLYING_PRICE_FIELD_NUMBER: _ClassVar[int]
    INTEREST_RATE_FIELD_NUMBER: _ClassVar[int]
    DAYS_TO_EXPIRY_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    delta: float
    gamma: float
    theta: float
    vega: float
    rho: float
    implied_volatility: float
    theoretical_value: float
    underlying_price: float
    interest_rate: float
    days_to_expiry: int
    def __init__(self, symbol: _Optional[str] = ..., delta: _Optional[float] = ..., gamma: _Optional[float] = ..., theta: _Optional[float] = ..., vega: _Optional[float] = ..., rho: _Optional[float] = ..., implied_volatility: _Optional[float] = ..., theoretical_value: _Optional[float] = ..., underlying_price: _Optional[float] = ..., interest_rate: _Optional[float] = ..., days_to_expiry: _Optional[int] = ...) -> None: ...

class OrderUpdateEvent(_message.Message):
    __slots__ = ("order_id", "symbol", "status", "side", "order_type", "quantity", "filled_quantity", "remaining_quantity", "limit_price", "stop_price", "avg_fill_price", "created_at_us", "updated_at_us", "reject_reason", "metadata")
    class MetadataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SIDE_FIELD_NUMBER: _ClassVar[int]
    ORDER_TYPE_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    FILLED_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    REMAINING_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    LIMIT_PRICE_FIELD_NUMBER: _ClassVar[int]
    STOP_PRICE_FIELD_NUMBER: _ClassVar[int]
    AVG_FILL_PRICE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_US_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_US_FIELD_NUMBER: _ClassVar[int]
    REJECT_REASON_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    order_id: str
    symbol: str
    status: _common_pb2.OrderStatus
    side: _common_pb2.OrderSide
    order_type: _common_pb2.OrderType
    quantity: float
    filled_quantity: float
    remaining_quantity: float
    limit_price: float
    stop_price: float
    avg_fill_price: float
    created_at_us: int
    updated_at_us: int
    reject_reason: str
    metadata: _containers.ScalarMap[str, str]
    def __init__(self, order_id: _Optional[str] = ..., symbol: _Optional[str] = ..., status: _Optional[_Union[_common_pb2.OrderStatus, str]] = ..., side: _Optional[_Union[_common_pb2.OrderSide, str]] = ..., order_type: _Optional[_Union[_common_pb2.OrderType, str]] = ..., quantity: _Optional[float] = ..., filled_quantity: _Optional[float] = ..., remaining_quantity: _Optional[float] = ..., limit_price: _Optional[float] = ..., stop_price: _Optional[float] = ..., avg_fill_price: _Optional[float] = ..., created_at_us: _Optional[int] = ..., updated_at_us: _Optional[int] = ..., reject_reason: _Optional[str] = ..., metadata: _Optional[_Mapping[str, str]] = ...) -> None: ...

class PositionUpdateEvent(_message.Message):
    __slots__ = ("symbol", "quantity", "avg_price", "unrealized_pnl", "realized_pnl", "market_value", "current_price", "bid", "ask")
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    AVG_PRICE_FIELD_NUMBER: _ClassVar[int]
    UNREALIZED_PNL_FIELD_NUMBER: _ClassVar[int]
    REALIZED_PNL_FIELD_NUMBER: _ClassVar[int]
    MARKET_VALUE_FIELD_NUMBER: _ClassVar[int]
    CURRENT_PRICE_FIELD_NUMBER: _ClassVar[int]
    BID_FIELD_NUMBER: _ClassVar[int]
    ASK_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    quantity: float
    avg_price: float
    unrealized_pnl: float
    realized_pnl: float
    market_value: float
    current_price: float
    bid: float
    ask: float
    def __init__(self, symbol: _Optional[str] = ..., quantity: _Optional[float] = ..., avg_price: _Optional[float] = ..., unrealized_pnl: _Optional[float] = ..., realized_pnl: _Optional[float] = ..., market_value: _Optional[float] = ..., current_price: _Optional[float] = ..., bid: _Optional[float] = ..., ask: _Optional[float] = ...) -> None: ...

class AccountUpdateEvent(_message.Message):
    __slots__ = ("cash_balance", "portfolio_value", "buying_power", "initial_margin", "maintenance_margin", "margin_used", "daily_pnl", "total_pnl", "leverage", "risk_metrics")
    class RiskMetricsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: float
        def __init__(self, key: _Optional[str] = ..., value: _Optional[float] = ...) -> None: ...
    CASH_BALANCE_FIELD_NUMBER: _ClassVar[int]
    PORTFOLIO_VALUE_FIELD_NUMBER: _ClassVar[int]
    BUYING_POWER_FIELD_NUMBER: _ClassVar[int]
    INITIAL_MARGIN_FIELD_NUMBER: _ClassVar[int]
    MAINTENANCE_MARGIN_FIELD_NUMBER: _ClassVar[int]
    MARGIN_USED_FIELD_NUMBER: _ClassVar[int]
    DAILY_PNL_FIELD_NUMBER: _ClassVar[int]
    TOTAL_PNL_FIELD_NUMBER: _ClassVar[int]
    LEVERAGE_FIELD_NUMBER: _ClassVar[int]
    RISK_METRICS_FIELD_NUMBER: _ClassVar[int]
    cash_balance: float
    portfolio_value: float
    buying_power: float
    initial_margin: float
    maintenance_margin: float
    margin_used: float
    daily_pnl: float
    total_pnl: float
    leverage: float
    risk_metrics: _containers.ScalarMap[str, float]
    def __init__(self, cash_balance: _Optional[float] = ..., portfolio_value: _Optional[float] = ..., buying_power: _Optional[float] = ..., initial_margin: _Optional[float] = ..., maintenance_margin: _Optional[float] = ..., margin_used: _Optional[float] = ..., daily_pnl: _Optional[float] = ..., total_pnl: _Optional[float] = ..., leverage: _Optional[float] = ..., risk_metrics: _Optional[_Mapping[str, float]] = ...) -> None: ...

class TradeEvent(_message.Message):
    __slots__ = ("trade_id", "order_id", "symbol", "side", "quantity", "price", "timestamp_us", "commission", "fees")
    TRADE_ID_FIELD_NUMBER: _ClassVar[int]
    ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    SIDE_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_US_FIELD_NUMBER: _ClassVar[int]
    COMMISSION_FIELD_NUMBER: _ClassVar[int]
    FEES_FIELD_NUMBER: _ClassVar[int]
    trade_id: str
    order_id: str
    symbol: str
    side: _common_pb2.OrderSide
    quantity: float
    price: float
    timestamp_us: int
    commission: float
    fees: float
    def __init__(self, trade_id: _Optional[str] = ..., order_id: _Optional[str] = ..., symbol: _Optional[str] = ..., side: _Optional[_Union[_common_pb2.OrderSide, str]] = ..., quantity: _Optional[float] = ..., price: _Optional[float] = ..., timestamp_us: _Optional[int] = ..., commission: _Optional[float] = ..., fees: _Optional[float] = ...) -> None: ...

class SystemEvent(_message.Message):
    __slots__ = ("type", "message", "details")
    class DetailsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    TYPE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    DETAILS_FIELD_NUMBER: _ClassVar[int]
    type: _common_pb2.SystemEventType
    message: str
    details: _containers.ScalarMap[str, str]
    def __init__(self, type: _Optional[_Union[_common_pb2.SystemEventType, str]] = ..., message: _Optional[str] = ..., details: _Optional[_Mapping[str, str]] = ...) -> None: ...

class HistoricalDataRequest(_message.Message):
    __slots__ = ("symbol", "start_timestamp_us", "end_timestamp_us", "bar_size", "limit")
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    START_TIMESTAMP_US_FIELD_NUMBER: _ClassVar[int]
    END_TIMESTAMP_US_FIELD_NUMBER: _ClassVar[int]
    BAR_SIZE_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    start_timestamp_us: int
    end_timestamp_us: int
    bar_size: str
    limit: int
    def __init__(self, symbol: _Optional[str] = ..., start_timestamp_us: _Optional[int] = ..., end_timestamp_us: _Optional[int] = ..., bar_size: _Optional[str] = ..., limit: _Optional[int] = ...) -> None: ...

class HistoricalDataResponse(_message.Message):
    __slots__ = ("symbol", "bar_size", "bars")
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    BAR_SIZE_FIELD_NUMBER: _ClassVar[int]
    BARS_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    bar_size: str
    bars: _containers.RepeatedCompositeFieldContainer[_common_pb2.Bar]
    def __init__(self, symbol: _Optional[str] = ..., bar_size: _Optional[str] = ..., bars: _Optional[_Iterable[_Union[_common_pb2.Bar, _Mapping]]] = ...) -> None: ...

class MarketDepthRequest(_message.Message):
    __slots__ = ("symbol", "depth")
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    DEPTH_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    depth: int
    def __init__(self, symbol: _Optional[str] = ..., depth: _Optional[int] = ...) -> None: ...

class MarketDepthResponse(_message.Message):
    __slots__ = ("symbol", "timestamp_us", "bids", "asks")
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_US_FIELD_NUMBER: _ClassVar[int]
    BIDS_FIELD_NUMBER: _ClassVar[int]
    ASKS_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    timestamp_us: int
    bids: _containers.RepeatedCompositeFieldContainer[_common_pb2.PriceLevel]
    asks: _containers.RepeatedCompositeFieldContainer[_common_pb2.PriceLevel]
    def __init__(self, symbol: _Optional[str] = ..., timestamp_us: _Optional[int] = ..., bids: _Optional[_Iterable[_Union[_common_pb2.PriceLevel, _Mapping]]] = ..., asks: _Optional[_Iterable[_Union[_common_pb2.PriceLevel, _Mapping]]] = ...) -> None: ...
