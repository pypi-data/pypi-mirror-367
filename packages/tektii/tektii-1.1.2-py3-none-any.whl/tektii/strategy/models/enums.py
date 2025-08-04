"""Trading enums with type safety and conversion utilities.

This module provides Python enums that mirror the proto enums, with built-in
conversion methods for seamless interoperability with the gRPC layer.
"""

from __future__ import annotations

from enum import Enum, IntEnum
from typing import TypeVar, cast

from tektii.strategy.grpc import common_pb2

T = TypeVar("T", bound="ProtoEnum")


class ProtoEnum(IntEnum):
    """Base class for proto-compatible enums with conversion utilities."""

    @classmethod
    def from_proto(cls: type[T], value: int) -> T:
        """Create enum from proto value.

        Args:
            value: Proto enum value

        Returns:
            Enum instance

        Raises:
            ValueError: If value is not valid
        """
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"Invalid {cls.__name__} proto value: {value}")

    def to_proto(self) -> int:
        """Convert to proto enum value.

        Returns:
            Proto enum value
        """
        return self.value

    @classmethod
    def from_string(cls: type[T], value: str) -> T:
        """Create enum from string representation.

        Args:
            value: String representation (case-insensitive)

        Returns:
            Enum instance

        Raises:
            ValueError: If string is not valid
        """
        value_upper = value.upper()
        for member in cls:
            if member.name == value_upper:
                return member

        # Handle special cases
        if hasattr(cls, "_aliases"):
            aliases = cls._aliases()  # type: ignore[attr-defined]
            if value_upper in aliases:
                return cast(T, aliases[value_upper])

        raise ValueError(f"Invalid {cls.__name__}: {value}")

    def __str__(self) -> str:
        """Return string representation without enum prefix."""
        return self.name


class OrderStatus(ProtoEnum):
    """Order status enumeration.

    Represents the current state of an order in its lifecycle.
    """

    UNKNOWN = common_pb2.ORDER_STATUS_UNKNOWN
    PENDING = common_pb2.ORDER_STATUS_PENDING
    SUBMITTED = common_pb2.ORDER_STATUS_SUBMITTED
    ACCEPTED = common_pb2.ORDER_STATUS_ACCEPTED
    PARTIALLY_FILLED = common_pb2.ORDER_STATUS_PARTIAL
    PARTIAL = common_pb2.ORDER_STATUS_PARTIAL  # Alias for PARTIALLY_FILLED
    FILLED = common_pb2.ORDER_STATUS_FILLED
    CANCELED = common_pb2.ORDER_STATUS_CANCELED
    CANCELLED = common_pb2.ORDER_STATUS_CANCELED  # Alias for CANCELED
    REJECTED = common_pb2.ORDER_STATUS_REJECTED
    EXPIRED = common_pb2.ORDER_STATUS_EXPIRED

    @classmethod
    def _aliases(cls) -> dict[str, OrderStatus]:
        """Return string aliases for special cases."""
        return {
            "CANCELLED": cls.CANCELED,  # Accept both spellings
            "PARTIALLY_FILLED": cls.PARTIAL,
        }

    def is_terminal(self) -> bool:
        """Check if this is a terminal status (order is done).

        Returns:
            True if order is in terminal state
        """
        return self in (
            OrderStatus.FILLED,
            OrderStatus.CANCELED,
            OrderStatus.REJECTED,
            OrderStatus.EXPIRED,
        )

    def is_active(self) -> bool:
        """Check if order is still active.

        Returns:
            True if order can still be executed
        """
        return self in (
            OrderStatus.PENDING,
            OrderStatus.SUBMITTED,
            OrderStatus.ACCEPTED,
            OrderStatus.PARTIAL,
        )


class OrderSide(ProtoEnum):
    """Order side enumeration.

    Indicates whether an order is to buy or sell.
    """

    UNKNOWN = common_pb2.ORDER_SIDE_UNKNOWN
    BUY = common_pb2.ORDER_SIDE_BUY
    SELL = common_pb2.ORDER_SIDE_SELL

    def opposite(self) -> OrderSide:
        """Get the opposite side.

        Returns:
            Opposite order side

        Raises:
            ValueError: If side is UNKNOWN
        """
        if self == OrderSide.BUY:
            return OrderSide.SELL
        elif self == OrderSide.SELL:
            return OrderSide.BUY
        else:
            raise ValueError("Cannot get opposite of UNKNOWN side")


class OrderType(ProtoEnum):
    """Order type enumeration.

    Specifies how an order should be executed.
    """

    UNKNOWN = common_pb2.ORDER_TYPE_UNKNOWN
    MARKET = common_pb2.ORDER_TYPE_MARKET
    LIMIT = common_pb2.ORDER_TYPE_LIMIT
    STOP = common_pb2.ORDER_TYPE_STOP
    STOP_LIMIT = common_pb2.ORDER_TYPE_STOP_LIMIT

    def requires_limit_price(self) -> bool:
        """Check if this order type requires a limit price.

        Returns:
            True if limit price is required
        """
        return self in (OrderType.LIMIT, OrderType.STOP_LIMIT)

    def requires_stop_price(self) -> bool:
        """Check if this order type requires a stop price.

        Returns:
            True if stop price is required
        """
        return self in (OrderType.STOP, OrderType.STOP_LIMIT)


class OrderIntent(ProtoEnum):
    """Order intent enumeration.

    Indicates the purpose of an order for tracking and risk management.
    """

    UNKNOWN = common_pb2.ORDER_INTENT_UNKNOWN
    OPEN = common_pb2.ORDER_INTENT_OPEN
    CLOSE = common_pb2.ORDER_INTENT_CLOSE
    STOP_LOSS = common_pb2.ORDER_INTENT_STOP_LOSS
    TAKE_PROFIT = common_pb2.ORDER_INTENT_TAKE_PROFIT

    def is_protective(self) -> bool:
        """Check if this is a protective order intent.

        Returns:
            True if order is protective (stop loss or take profit)
        """
        return self in (OrderIntent.STOP_LOSS, OrderIntent.TAKE_PROFIT)


class TimeInForce(ProtoEnum):
    """Time in force enumeration.

    Specifies how long an order remains active.
    """

    UNKNOWN = common_pb2.TIME_IN_FORCE_UNKNOWN
    DAY = common_pb2.TIME_IN_FORCE_DAY
    GTC = common_pb2.TIME_IN_FORCE_GTC
    IOC = common_pb2.TIME_IN_FORCE_IOC
    FOK = common_pb2.TIME_IN_FORCE_FOK

    def is_immediate(self) -> bool:
        """Check if this is an immediate-or-cancel type.

        Returns:
            True if order must execute immediately or cancel
        """
        return self in (TimeInForce.IOC, TimeInForce.FOK)


# Note: SystemEventType, RejectCode, ValidationErrorCode, and ValidationWarningCode
# have been moved to tektii.strategy.models.errors


# Additional enums from market_data.proto and missing from tests


class TickType(IntEnum):
    """Tick type enumeration.

    Indicates the type of data in a tick.
    """

    UNKNOWN = 0
    QUOTE = 1
    TRADE = 2
    QUOTE_AND_TRADE = 3


class BarType(IntEnum):
    """Bar type enumeration.

    Indicates how bars are aggregated.
    """

    UNKNOWN = 0
    TIME = 1
    TICK = 2
    VOLUME = 3
    DOLLAR = 4


# Missing enums referenced in tests but not yet implemented


class PositionSide(str, Enum):
    """Position side enumeration.

    Indicates the direction of a position.
    """

    LONG = "LONG"
    SHORT = "SHORT"
    FLAT = "FLAT"

    @classmethod
    def from_quantity(cls, quantity: float) -> PositionSide:
        """Determine position side from quantity.

        Args:
            quantity: Position quantity

        Returns:
            Position side based on quantity sign
        """
        if quantity > 0:
            return cls.LONG
        elif quantity < 0:
            return cls.SHORT
        else:
            return cls.FLAT


class AssetClass(str, Enum):
    """Asset class enumeration.

    Represents different types of financial instruments.
    """

    EQUITY = "EQUITY"
    OPTION = "OPTION"
    FUTURE = "FUTURE"
    FOREX = "FOREX"
    CRYPTO = "CRYPTO"


class Exchange(str, Enum):
    """Exchange enumeration.

    Represents different trading venues.
    """

    NYSE = "NYSE"
    NASDAQ = "NASDAQ"
    ARCA = "ARCA"
    BATS = "BATS"
    IEX = "IEX"
    CBOE = "CBOE"
    ISE = "ISE"
    PHLX = "PHLX"


class OptionType(str, Enum):
    """Option type enumeration.

    Represents call and put options.
    """

    CALL = "CALL"
    PUT = "PUT"
