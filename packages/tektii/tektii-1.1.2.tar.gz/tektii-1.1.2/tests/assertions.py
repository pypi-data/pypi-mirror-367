"""Custom assertions for trading-specific tests."""

from decimal import Decimal

from tektii.strategy.models.enums import OrderSide, OrderType
from tektii.strategy.models.orders import Order


def assert_decimal_equal(actual: Decimal, expected: Decimal, places: int = 6) -> None:
    """Assert decimal equality with precision tolerance.

    Args:
        actual: The actual decimal value
        expected: The expected decimal value
        places: Number of decimal places for comparison precision
    """
    tolerance = Decimal(f"1e-{places}")
    diff = abs(actual - expected)
    assert diff < tolerance, f"Decimal values not equal within {places} places: {actual} != {expected} (diff: {diff})"


def assert_order_valid(order: Order) -> None:
    """Assert order meets all validation criteria.

    Args:
        order: The order to validate
    """
    # Basic required fields
    assert order.symbol, "Order must have a symbol"
    assert order.quantity > 0, "Order quantity must be positive"
    assert order.side in [
        OrderSide.BUY,
        OrderSide.SELL,
    ], f"Invalid order side: {order.side}"
    assert order.order_type in OrderType, f"Invalid order type: {order.order_type}"

    # Type-specific validations
    if order.order_type == OrderType.LIMIT:
        assert order.limit_price is not None, "Limit order must have a limit price"
        assert order.limit_price > 0, "Limit price must be positive"

    if order.order_type == OrderType.STOP:
        assert order.stop_price is not None, "Stop order must have a stop price"
        assert order.stop_price > 0, "Stop price must be positive"

    if order.order_type == OrderType.STOP_LIMIT:
        assert order.limit_price is not None, "Stop-limit order must have a limit price"
        assert order.stop_price is not None, "Stop-limit order must have a stop price"
        assert order.limit_price > 0, "Limit price must be positive"
        assert order.stop_price > 0, "Stop price must be positive"


def assert_price_within_range(price: Decimal, low: Decimal, high: Decimal, inclusive: bool = True) -> None:
    """Assert price is within a specified range.

    Args:
        price: The price to check
        low: Lower bound
        high: Upper bound
        inclusive: Whether bounds are inclusive
    """
    if inclusive:
        assert low <= price <= high, f"Price {price} not in range [{low}, {high}]"
    else:
        assert low < price < high, f"Price {price} not in range ({low}, {high})"


def assert_proto_conversion_preserves_data(original: any, proto_type: type, model_type: type) -> None:
    """Assert that converting to proto and back preserves all data.

    Args:
        original: The original model instance
        proto_type: The protobuf message type
        model_type: The model class with from_proto method
    """
    # Convert to proto
    proto = original.to_proto()
    assert isinstance(proto, proto_type), f"Expected {proto_type}, got {type(proto)}"

    # Convert back
    restored = model_type.from_proto(proto)

    # Compare key fields based on type
    if hasattr(original, "symbol"):
        assert restored.symbol == original.symbol

    if hasattr(original, "quantity"):
        assert_decimal_equal(restored.quantity, original.quantity)

    if hasattr(original, "limit_price") and original.limit_price is not None:
        assert_decimal_equal(restored.limit_price, original.limit_price)

    if hasattr(original, "stop_price") and original.stop_price is not None:
        assert_decimal_equal(restored.stop_price, original.stop_price)

    if hasattr(original, "side"):
        assert restored.side == original.side

    if hasattr(original, "order_type"):
        assert restored.order_type == original.order_type


def assert_financial_calculation_accurate(result: Decimal, expected: Decimal, tolerance_percent: Decimal | None = None) -> None:
    """Assert financial calculation is within acceptable tolerance.

    Args:
        result: The calculated result
        expected: The expected value
        tolerance_percent: Acceptable tolerance as a percentage (default 0.01%)
    """
    if tolerance_percent is None:
        tolerance_percent = Decimal("0.0001")

    if expected == 0:
        assert result == 0, f"Expected 0, got {result}"
        return

    percent_diff = abs((result - expected) / expected) * 100
    assert percent_diff <= tolerance_percent, f"Calculation error {percent_diff:.4f}% exceeds tolerance {tolerance_percent}%"
