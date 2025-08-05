"""Error types and codes for the Tektii SDK.

This module consolidates all error-related enumerations and classes
from the proto specification, providing a centralized location for
error handling types.
"""

from typing import Optional

from tektii.strategy.grpc import common_pb2
from tektii.strategy.models.enums import ProtoEnum


class RejectCode(ProtoEnum):
    """Reject code enumeration.

    Provides specific reasons for order rejections.
    """

    UNKNOWN = common_pb2.REJECT_CODE_UNKNOWN
    INSUFFICIENT_MARGIN = common_pb2.REJECT_CODE_INSUFFICIENT_MARGIN
    POSITION_LIMIT = common_pb2.REJECT_CODE_POSITION_LIMIT
    INVALID_SYMBOL = common_pb2.REJECT_CODE_INVALID_SYMBOL
    MARKET_CLOSED = common_pb2.REJECT_CODE_MARKET_CLOSED
    INVALID_QUANTITY = common_pb2.REJECT_CODE_INVALID_QUANTITY
    INVALID_PRICE = common_pb2.REJECT_CODE_INVALID_PRICE
    RATE_LIMIT = common_pb2.REJECT_CODE_RATE_LIMIT
    DUPLICATE_ORDER = common_pb2.REJECT_CODE_DUPLICATE_ORDER
    ACCOUNT_RESTRICTED = common_pb2.REJECT_CODE_ACCOUNT_RESTRICTED
    ORDER_NOT_FOUND = common_pb2.REJECT_CODE_ORDER_NOT_FOUND
    ORDER_NOT_MODIFIABLE = common_pb2.REJECT_CODE_ORDER_NOT_MODIFIABLE
    RISK_CHECK_FAILED = common_pb2.REJECT_CODE_RISK_CHECK_FAILED

    @property
    def is_retryable(self) -> bool:
        """Check if the rejection is potentially retryable."""
        return self in (
            RejectCode.RATE_LIMIT,
            RejectCode.MARKET_CLOSED,
        )


class ValidationErrorCode(ProtoEnum):
    """Validation error code enumeration.

    For pre-trade validation errors.
    """

    UNKNOWN = common_pb2.VALIDATION_ERROR_UNKNOWN
    INVALID_SYMBOL = common_pb2.VALIDATION_ERROR_INVALID_SYMBOL
    INVALID_QUANTITY = common_pb2.VALIDATION_ERROR_INVALID_QUANTITY
    INVALID_PRICE = common_pb2.VALIDATION_ERROR_INVALID_PRICE
    MISSING_REQUIRED_FIELD = common_pb2.VALIDATION_ERROR_MISSING_REQUIRED_FIELD
    CONFLICTING_FIELDS = common_pb2.VALIDATION_ERROR_CONFLICTING_FIELDS


class ValidationWarningCode(ProtoEnum):
    """Validation warning code enumeration.

    For non-blocking validation warnings.
    """

    UNKNOWN = common_pb2.VALIDATION_WARNING_UNKNOWN
    HIGH_CONCENTRATION = common_pb2.VALIDATION_WARNING_HIGH_CONCENTRATION
    UNUSUAL_SIZE = common_pb2.VALIDATION_WARNING_UNUSUAL_SIZE
    FAR_FROM_MARKET = common_pb2.VALIDATION_WARNING_FAR_FROM_MARKET
    LOW_LIQUIDITY = common_pb2.VALIDATION_WARNING_LOW_LIQUIDITY
    HIGH_VOLATILITY = common_pb2.VALIDATION_WARNING_HIGH_VOLATILITY


class SystemEventType(ProtoEnum):
    """System event type enumeration.

    Categorizes system-level events.
    """

    UNKNOWN = common_pb2.SYSTEM_EVENT_UNKNOWN
    CONNECTED = common_pb2.SYSTEM_EVENT_CONNECTED
    DISCONNECTED = common_pb2.SYSTEM_EVENT_DISCONNECTED
    ERROR = common_pb2.SYSTEM_EVENT_ERROR
    WARNING = common_pb2.SYSTEM_EVENT_WARNING
    INFO = common_pb2.SYSTEM_EVENT_INFO


class TektiiError(Exception):
    """Base exception for all Tektii SDK errors."""

    pass


class OrderValidationError(TektiiError):
    """Raised when order validation fails."""

    def __init__(
        self,
        message: str,
        code: Optional[ValidationErrorCode] = None,
        field: Optional[str] = None,
    ):
        """Initialize an OrderValidationError."""
        super().__init__(message)
        self.code = code
        self.field = field


class OrderRejectionError(TektiiError):
    """Raised when an order is rejected by the system."""

    def __init__(
        self,
        message: str,
        code: Optional[RejectCode] = None,
        order_id: Optional[str] = None,
    ):
        """Initialize an OrderRejectionError."""
        super().__init__(message)
        self.code = code
        self.order_id = order_id


class StrategyError(TektiiError):
    """Raised when a strategy encounters an error."""

    pass


class ConnectionError(TektiiError):
    """Raised when connection issues occur."""

    pass


class ConfigurationError(TektiiError):
    """Raised when configuration is invalid."""

    pass


__all__ = [
    # Enumerations
    "RejectCode",
    "ValidationErrorCode",
    "ValidationWarningCode",
    "SystemEventType",
    # Exceptions
    "TektiiError",
    "OrderValidationError",
    "OrderRejectionError",
    "StrategyError",
    "ConnectionError",
    "ConfigurationError",
]
