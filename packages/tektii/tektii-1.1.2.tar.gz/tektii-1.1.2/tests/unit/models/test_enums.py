"""Unit tests for enum models."""

import pytest

from tektii.strategy.models.enums import AssetClass, Exchange, OptionType, OrderIntent, OrderSide, OrderStatus, OrderType, PositionSide, TimeInForce


class TestOrderSide:
    """Test OrderSide enum."""

    def test_order_side_values(self):
        """Test OrderSide has expected proto values."""
        # Proto enums use int values, not strings
        assert OrderSide.BUY.value == 1  # ORDER_SIDE_BUY
        assert OrderSide.SELL.value == 2  # ORDER_SIDE_SELL

    def test_order_side_string_representation(self):
        """Test OrderSide string representation."""
        assert str(OrderSide.BUY) == "BUY"
        assert str(OrderSide.SELL) == "SELL"

    def test_order_side_from_string(self):
        """Test creating OrderSide from string."""
        assert OrderSide.from_string("BUY") == OrderSide.BUY
        assert OrderSide.from_string("SELL") == OrderSide.SELL

    def test_order_side_invalid_value(self):
        """Test invalid OrderSide value raises error."""
        with pytest.raises(ValueError, match="Invalid OrderSide"):
            OrderSide.from_string("INVALID")

    def test_order_side_case_sensitivity(self):
        """Test OrderSide is case insensitive."""
        # from_string should handle case conversion
        assert OrderSide.from_string("buy") == OrderSide.BUY
        assert OrderSide.from_string("sell") == OrderSide.SELL

    def test_order_side_proto_conversion(self):
        """Test OrderSide proto conversion."""
        # Test conversion to proto value
        assert OrderSide.BUY.to_proto() == 1  # ORDER_SIDE_BUY
        assert OrderSide.SELL.to_proto() == 2  # ORDER_SIDE_SELL

        # Test conversion from proto value
        assert OrderSide.from_proto(1) == OrderSide.BUY
        assert OrderSide.from_proto(2) == OrderSide.SELL

    def test_order_side_from_proto_invalid(self):
        """Test invalid proto value raises error."""
        with pytest.raises(ValueError, match="Invalid OrderSide proto value"):
            OrderSide.from_proto(99)

    def test_order_side_opposite(self):
        """Test getting opposite side."""
        assert OrderSide.BUY.opposite() == OrderSide.SELL
        assert OrderSide.SELL.opposite() == OrderSide.BUY


class TestOrderType:
    """Test OrderType enum."""

    def test_order_type_values(self):
        """Test OrderType has expected proto values."""
        assert OrderType.MARKET.value == 1  # ORDER_TYPE_MARKET
        assert OrderType.LIMIT.value == 2  # ORDER_TYPE_LIMIT
        assert OrderType.STOP.value == 3  # ORDER_TYPE_STOP
        assert OrderType.STOP_LIMIT.value == 4  # ORDER_TYPE_STOP_LIMIT

    def test_order_type_string_representation(self):
        """Test OrderType string representation."""
        assert str(OrderType.MARKET) == "MARKET"
        assert str(OrderType.LIMIT) == "LIMIT"
        assert str(OrderType.STOP) == "STOP"
        assert str(OrderType.STOP_LIMIT) == "STOP_LIMIT"

    def test_order_type_from_string(self):
        """Test creating OrderType from string."""
        assert OrderType.from_string("MARKET") == OrderType.MARKET
        assert OrderType.from_string("LIMIT") == OrderType.LIMIT
        assert OrderType.from_string("STOP") == OrderType.STOP
        assert OrderType.from_string("STOP_LIMIT") == OrderType.STOP_LIMIT

    def test_order_type_proto_conversion(self):
        """Test OrderType proto conversion."""
        # Test conversion to proto value
        assert OrderType.MARKET.to_proto() == 1  # ORDER_TYPE_MARKET
        assert OrderType.LIMIT.to_proto() == 2  # ORDER_TYPE_LIMIT
        assert OrderType.STOP.to_proto() == 3  # ORDER_TYPE_STOP
        assert OrderType.STOP_LIMIT.to_proto() == 4  # ORDER_TYPE_STOP_LIMIT

        # Test conversion from proto value
        assert OrderType.from_proto(1) == OrderType.MARKET
        assert OrderType.from_proto(2) == OrderType.LIMIT
        assert OrderType.from_proto(3) == OrderType.STOP
        assert OrderType.from_proto(4) == OrderType.STOP_LIMIT

    def test_order_type_requires_price(self):
        """Test which order types require prices."""
        # Market orders don't require prices
        assert not OrderType.MARKET.requires_limit_price()
        assert not OrderType.MARKET.requires_stop_price()

        # Limit orders require limit price
        assert OrderType.LIMIT.requires_limit_price()
        assert not OrderType.LIMIT.requires_stop_price()

        # Stop orders require stop price
        assert not OrderType.STOP.requires_limit_price()
        assert OrderType.STOP.requires_stop_price()

        # Stop limit orders require both
        assert OrderType.STOP_LIMIT.requires_limit_price()
        assert OrderType.STOP_LIMIT.requires_stop_price()


class TestOrderStatus:
    """Test OrderStatus enum."""

    def test_order_status_values(self):
        """Test OrderStatus has expected proto values."""
        expected_statuses = [
            ("PENDING", 1),
            ("SUBMITTED", 2),
            ("ACCEPTED", 3),
            ("PARTIALLY_FILLED", 4),
            ("FILLED", 5),
            ("CANCELED", 6),
            ("REJECTED", 7),
            ("EXPIRED", 8),
        ]

        for status_name, expected_value in expected_statuses:
            status = getattr(OrderStatus, status_name)
            assert status.value == expected_value

    def test_order_status_terminal_states(self):
        """Test identifying terminal order states."""
        terminal_states = [OrderStatus.REJECTED, OrderStatus.FILLED, OrderStatus.CANCELED, OrderStatus.EXPIRED]

        active_states = [OrderStatus.PENDING, OrderStatus.SUBMITTED, OrderStatus.ACCEPTED, OrderStatus.PARTIALLY_FILLED]

        # Verify terminal states
        for status in terminal_states:
            assert status.is_terminal()
            assert not status.is_active()

        # Verify active states
        for status in active_states:
            assert not status.is_terminal()
            assert status.is_active()

    def test_order_status_from_string_variations(self):
        """Test OrderStatus handles common variations."""
        # Standard values should work
        assert OrderStatus.from_string("FILLED") == OrderStatus.FILLED
        assert OrderStatus.from_string("CANCELED") == OrderStatus.CANCELED

        # Test aliases
        assert OrderStatus.from_string("CANCELLED") == OrderStatus.CANCELED
        assert OrderStatus.from_string("PARTIALLY_FILLED") == OrderStatus.PARTIALLY_FILLED

    def test_order_status_aliases(self):
        """Test OrderStatus aliases work correctly."""
        # CANCELLED is alias for CANCELED
        assert OrderStatus.CANCELLED == OrderStatus.CANCELED
        # PARTIAL is alias for PARTIALLY_FILLED
        assert OrderStatus.PARTIAL == OrderStatus.PARTIALLY_FILLED


class TestTimeInForce:
    """Test TimeInForce enum."""

    def test_time_in_force_values(self):
        """Test TimeInForce has expected proto values."""
        assert TimeInForce.DAY.value == 1  # TIME_IN_FORCE_DAY
        assert TimeInForce.GTC.value == 2  # TIME_IN_FORCE_GTC
        assert TimeInForce.IOC.value == 3  # TIME_IN_FORCE_IOC
        assert TimeInForce.FOK.value == 4  # TIME_IN_FORCE_FOK

    def test_time_in_force_string_representation(self):
        """Test TimeInForce string representation."""
        assert str(TimeInForce.DAY) == "DAY"
        assert str(TimeInForce.GTC) == "GTC"
        assert str(TimeInForce.IOC) == "IOC"
        assert str(TimeInForce.FOK) == "FOK"

    def test_time_in_force_proto_conversion(self):
        """Test TimeInForce proto conversion."""
        # Test conversion to proto value
        assert TimeInForce.DAY.to_proto() == 1  # TIME_IN_FORCE_DAY
        assert TimeInForce.GTC.to_proto() == 2  # TIME_IN_FORCE_GTC
        assert TimeInForce.IOC.to_proto() == 3  # TIME_IN_FORCE_IOC
        assert TimeInForce.FOK.to_proto() == 4  # TIME_IN_FORCE_FOK

        # Test conversion from proto value
        assert TimeInForce.from_proto(1) == TimeInForce.DAY
        assert TimeInForce.from_proto(2) == TimeInForce.GTC
        assert TimeInForce.from_proto(3) == TimeInForce.IOC
        assert TimeInForce.from_proto(4) == TimeInForce.FOK

    def test_time_in_force_immediate(self):
        """Test TimeInForce immediate orders."""
        # IOC and FOK are immediate
        assert TimeInForce.IOC.is_immediate()
        assert TimeInForce.FOK.is_immediate()

        # DAY and GTC are not immediate
        assert not TimeInForce.DAY.is_immediate()
        assert not TimeInForce.GTC.is_immediate()

    def test_time_in_force_descriptions(self):
        """Test TimeInForce enum has meaningful string values."""
        # DAY orders expire at market close
        assert str(TimeInForce.DAY) == "DAY"

        # GTC orders remain until filled or cancelled
        assert str(TimeInForce.GTC) == "GTC"

        # IOC orders fill immediately or cancel
        assert str(TimeInForce.IOC) == "IOC"

        # FOK orders fill completely or cancel
        assert str(TimeInForce.FOK) == "FOK"


class TestPositionSide:
    """Test PositionSide enum."""

    def test_position_side_values(self):
        """Test PositionSide has expected string values."""
        assert PositionSide.LONG.value == "LONG"
        assert PositionSide.SHORT.value == "SHORT"
        assert PositionSide.FLAT.value == "FLAT"

    def test_position_side_from_quantity(self):
        """Test determining position side from quantity."""
        # Positive quantity = long
        assert PositionSide.from_quantity(100) == PositionSide.LONG
        assert PositionSide.from_quantity(0.5) == PositionSide.LONG

        # Negative quantity = short
        assert PositionSide.from_quantity(-100) == PositionSide.SHORT
        assert PositionSide.from_quantity(-0.5) == PositionSide.SHORT

        # Zero quantity = flat
        assert PositionSide.from_quantity(0) == PositionSide.FLAT

    def test_position_side_transitions(self):
        """Test valid position side transitions."""
        # All transitions should be valid in the enum
        sides = [PositionSide.LONG, PositionSide.SHORT, PositionSide.FLAT]

        for from_side in sides:
            for to_side in sides:
                # Just verify both sides exist
                assert from_side in PositionSide
                assert to_side in PositionSide


class TestAssetClass:
    """Test AssetClass enum."""

    def test_asset_class_values(self):
        """Test AssetClass has expected string values."""
        expected_classes = ["EQUITY", "OPTION", "FUTURE", "FOREX", "CRYPTO"]

        for asset_class in expected_classes:
            assert hasattr(AssetClass, asset_class)
            assert getattr(AssetClass, asset_class).value == asset_class

    def test_asset_class_from_string(self):
        """Test creating AssetClass from string."""
        assert AssetClass("EQUITY") == AssetClass.EQUITY
        assert AssetClass("OPTION") == AssetClass.OPTION
        assert AssetClass("CRYPTO") == AssetClass.CRYPTO


class TestExchange:
    """Test Exchange enum."""

    def test_exchange_values(self):
        """Test Exchange has expected string values."""
        # Test some common exchanges
        expected_exchanges = ["NYSE", "NASDAQ", "ARCA", "BATS", "IEX"]

        for exchange in expected_exchanges:
            assert hasattr(Exchange, exchange)
            assert getattr(Exchange, exchange).value == exchange

    def test_exchange_categories(self):
        """Test exchange categories."""
        # US equity exchanges
        us_equity_exchanges = [Exchange.NYSE, Exchange.NASDAQ, Exchange.ARCA]
        for exchange in us_equity_exchanges:
            assert exchange in Exchange

        # Options exchanges
        options_exchanges = [Exchange.CBOE, Exchange.ISE, Exchange.PHLX]
        for exchange in options_exchanges:
            assert exchange in Exchange


class TestOptionType:
    """Test OptionType enum."""

    def test_option_type_values(self):
        """Test OptionType has expected string values."""
        assert OptionType.CALL.value == "CALL"
        assert OptionType.PUT.value == "PUT"

    def test_option_type_from_string(self):
        """Test creating OptionType from string."""
        assert OptionType("CALL") == OptionType.CALL
        assert OptionType("PUT") == OptionType.PUT

    def test_option_type_invalid_value(self):
        """Test invalid OptionType value raises error."""
        with pytest.raises(ValueError):
            OptionType("INVALID")


class TestOrderIntent:
    """Test OrderIntent enum."""

    def test_order_intent_values(self):
        """Test OrderIntent has expected proto values."""
        assert OrderIntent.OPEN.value == 1  # ORDER_INTENT_OPEN
        assert OrderIntent.CLOSE.value == 2  # ORDER_INTENT_CLOSE
        assert OrderIntent.STOP_LOSS.value == 3  # ORDER_INTENT_STOP_LOSS
        assert OrderIntent.TAKE_PROFIT.value == 4  # ORDER_INTENT_TAKE_PROFIT

    def test_order_intent_string_representation(self):
        """Test OrderIntent string representation."""
        assert str(OrderIntent.OPEN) == "OPEN"
        assert str(OrderIntent.CLOSE) == "CLOSE"
        assert str(OrderIntent.STOP_LOSS) == "STOP_LOSS"
        assert str(OrderIntent.TAKE_PROFIT) == "TAKE_PROFIT"

    def test_order_intent_proto_conversion(self):
        """Test OrderIntent proto conversion."""
        # Test conversion to proto value
        assert OrderIntent.OPEN.to_proto() == 1  # ORDER_INTENT_OPEN
        assert OrderIntent.CLOSE.to_proto() == 2  # ORDER_INTENT_CLOSE
        assert OrderIntent.STOP_LOSS.to_proto() == 3  # ORDER_INTENT_STOP_LOSS
        assert OrderIntent.TAKE_PROFIT.to_proto() == 4  # ORDER_INTENT_TAKE_PROFIT

        # Test conversion from proto value
        assert OrderIntent.from_proto(1) == OrderIntent.OPEN
        assert OrderIntent.from_proto(2) == OrderIntent.CLOSE
        assert OrderIntent.from_proto(3) == OrderIntent.STOP_LOSS
        assert OrderIntent.from_proto(4) == OrderIntent.TAKE_PROFIT

    def test_order_intent_protective(self):
        """Test OrderIntent protective order detection."""
        # STOP_LOSS and TAKE_PROFIT are protective
        assert OrderIntent.STOP_LOSS.is_protective()
        assert OrderIntent.TAKE_PROFIT.is_protective()

        # OPEN and CLOSE are not protective
        assert not OrderIntent.OPEN.is_protective()
        assert not OrderIntent.CLOSE.is_protective()

    def test_order_intent_use_cases(self):
        """Test OrderIntent use cases."""
        # OPEN - entering a new position
        assert str(OrderIntent.OPEN) == "OPEN"

        # CLOSE - exiting an existing position
        assert str(OrderIntent.CLOSE) == "CLOSE"

        # STOP_LOSS - protective stop loss
        assert str(OrderIntent.STOP_LOSS) == "STOP_LOSS"

        # TAKE_PROFIT - protective take profit
        assert str(OrderIntent.TAKE_PROFIT) == "TAKE_PROFIT"


class TestEnumCommonBehavior:
    """Test common behavior across all enums."""

    def test_proto_enums_are_int_enums(self):
        """Test proto enums inherit from IntEnum."""
        proto_enums = [OrderSide, OrderType, OrderStatus, TimeInForce, OrderIntent]

        for enum_class in proto_enums:
            # Get first value from enum
            first_value = list(enum_class)[0]
            # Verify it's an int
            assert isinstance(first_value.value, int)

    def test_string_enums_are_string_enums(self):
        """Test string enums have string values."""
        string_enums = [PositionSide, AssetClass, Exchange, OptionType]

        for enum_class in string_enums:
            # Get first value from enum
            first_value = list(enum_class)[0]
            # Verify it's a string
            assert isinstance(first_value.value, str)

    def test_enum_membership(self):
        """Test enum membership checking."""
        # Test 'in' operator
        assert OrderSide.BUY in OrderSide

        # Test isinstance
        assert isinstance(OrderSide.BUY, OrderSide)

    def test_enum_comparison(self):
        """Test enum comparison."""
        # Same enum values should be equal
        assert OrderSide.BUY == OrderSide.BUY
        assert OrderSide.BUY is OrderSide.BUY  # singleton

        # Different enum values should not be equal
        assert OrderSide.BUY != OrderSide.SELL

        # IntEnum values are equal to their int values (this is expected behavior)
        assert OrderSide.BUY == 1
        assert OrderSide.SELL == 2

    def test_enum_iteration(self):
        """Test iterating over enum values."""
        order_sides = list(OrderSide)
        assert len(order_sides) >= 2  # At least BUY and SELL
        assert OrderSide.BUY in order_sides
        assert OrderSide.SELL in order_sides

    def test_enum_string_representation(self):
        """Test enum string representation."""
        # str() should return the name for proto enums
        assert str(OrderSide.BUY) == "BUY"

        # repr() should include the enum class
        assert "OrderSide.BUY" in repr(OrderSide.BUY)
