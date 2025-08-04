"""Conversion utilities for handling Decimal to/from protobuf float conversions."""

from decimal import Decimal
from typing import Optional


def proto_from_decimal(value: Optional[Decimal]) -> float:
    """Convert a Decimal to float for protobuf serialization.

    Args:
        value: Decimal value or None

    Returns:
        float representation, or 0.0 if None
    """
    if value is None:
        return 0.0
    return float(value)


def decimal_from_proto(value: float) -> Optional[Decimal]:
    """Convert a protobuf float to Decimal.

    Args:
        value: float value from protobuf

    Returns:
        Decimal representation, or None if value is 0.0
    """
    if value == 0.0:
        return None
    return Decimal(str(value))


def decimal_from_proto_required(value: float) -> Decimal:
    """Convert a protobuf float to Decimal (required field).

    Args:
        value: float value from protobuf

    Returns:
        Decimal representation
    """
    return Decimal(str(value))
