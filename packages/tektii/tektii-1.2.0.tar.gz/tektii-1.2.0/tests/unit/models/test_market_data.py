"""Unit tests for market data models."""

from datetime import datetime
from decimal import Decimal

from tektii.strategy.models.enums import OptionType
from tektii.strategy.models.market_data import BarData, OptionGreeks, TickData
from tests.assertions import assert_decimal_equal
from tests.factories import BarDataFactory, OptionGreeksFactory, TickDataFactory


class TestTickData:
    """Test TickData model functionality."""

    def test_tick_data_creation_with_factory(self):
        """Test creating tick data with factory."""
        tick = TickDataFactory()

        assert tick.symbol
        assert tick.timestamp_us > 0
        assert tick.last > 0
        assert tick.bid < tick.ask  # Factory ensures valid spread
        assert tick.volume >= 0

    def test_tick_data_timestamp_conversion(self):
        """Test timestamp conversion to datetime."""
        timestamp_us = 1640995200000000  # 2022-01-01 00:00:00 UTC
        tick = TickDataFactory(timestamp_us=timestamp_us)

        expected_dt = datetime.fromtimestamp(timestamp_us / 1_000_000)
        assert tick.timestamp == expected_dt

    def test_tick_data_spread_calculation(self):
        """Test bid-ask spread calculation."""
        tick = TickDataFactory(bid=Decimal("149.99"), ask=Decimal("150.01"))

        spread = tick.ask - tick.bid
        assert_decimal_equal(spread, Decimal("0.02"))

    def test_tick_data_proto_conversion(self):
        """Test tick data proto conversion preserves available data."""
        from tektii.strategy.grpc import market_data_pb2

        tick = TickDataFactory(
            symbol="AAPL",
            last=Decimal("150.123"),
            bid=Decimal("150.100"),
            ask=Decimal("150.150"),
            bid_size=1000,
            ask_size=2000,
            exchange="NASDAQ",
        )

        proto = tick.to_proto()
        assert isinstance(proto, market_data_pb2.TickData)

        restored = TickData.from_proto(proto)
        assert restored.symbol == tick.symbol
        assert_decimal_equal(restored.last, tick.last)
        assert_decimal_equal(restored.bid, tick.bid)
        assert_decimal_equal(restored.ask, tick.ask)
        assert restored.bid_size == tick.bid_size
        assert restored.ask_size == tick.ask_size
        assert restored.exchange == tick.exchange
        # Note: volume and condition are not preserved in proto

    def test_tick_data_midpoint_calculation(self):
        """Test midpoint price calculation."""
        tick = TickDataFactory(bid=Decimal("100.00"), ask=Decimal("100.10"))

        midpoint = (tick.bid + tick.ask) / 2
        assert_decimal_equal(midpoint, Decimal("100.05"))

    def test_tick_data_validation(self):
        """Test tick data validation."""
        # Valid tick
        tick = TickDataFactory()
        assert tick.last > 0
        assert tick.bid > 0
        assert tick.ask > 0
        assert tick.bid < tick.ask

    def test_tick_data_string_representation(self):
        """Test tick data string representation."""
        tick = TickDataFactory(symbol="AAPL", last=Decimal("150.25"), bid=Decimal("150.24"), ask=Decimal("150.26"), volume=123456)

        str_repr = str(tick)
        assert "AAPL" in str_repr
        assert "150.25" in str_repr
        assert "123,456" in str_repr  # Volume is formatted with commas

    def test_tick_data_edge_cases(self):
        """Test tick data edge cases."""
        # Zero volume
        tick = TickDataFactory(volume=0)
        assert tick.volume == 0

        # No condition
        tick = TickDataFactory(condition=None)
        assert tick.condition is None

        # Very precise decimals
        tick = TickDataFactory(last=Decimal("123.456789"), bid=Decimal("123.456788"), ask=Decimal("123.456790"))
        assert_decimal_equal(tick.last, Decimal("123.456789"), places=6)


class TestBarData:
    """Test BarData model functionality."""

    def test_bar_data_creation_with_factory(self):
        """Test creating bar data with factory."""
        bar = BarDataFactory()

        assert bar.symbol
        assert bar.timestamp_us > 0
        assert bar.open > 0
        assert bar.high >= bar.low  # Factory ensures valid OHLC
        assert bar.high >= bar.open
        assert bar.high >= bar.close
        assert bar.low <= bar.open
        assert bar.low <= bar.close
        assert bar.volume >= 0

    def test_bar_data_ohlc_relationships(self):
        """Test OHLC relationships are maintained."""
        bar = BarDataFactory(open=Decimal("100"), high=Decimal("105"), low=Decimal("98"), close=Decimal("102"))

        # Verify OHLC relationships
        assert bar.low <= bar.open <= bar.high
        assert bar.low <= bar.close <= bar.high
        assert bar.low < bar.high

    def test_bar_data_typical_price(self):
        """Test typical price calculation (HLC/3)."""
        bar = BarDataFactory(high=Decimal("105"), low=Decimal("95"), close=Decimal("100"))

        typical_price = (bar.high + bar.low + bar.close) / 3
        assert_decimal_equal(typical_price, Decimal("100"))

    def test_bar_data_price_range(self):
        """Test price range calculation."""
        bar = BarDataFactory(high=Decimal("110"), low=Decimal("90"))

        price_range = bar.high - bar.low
        assert_decimal_equal(price_range, Decimal("20"))

    def test_bar_data_proto_conversion(self):
        """Test bar data proto conversion preserves all data."""
        from tektii.strategy.grpc import market_data_pb2

        bar = BarDataFactory(
            symbol="SPY",
            open=Decimal("400.50"),
            high=Decimal("401.75"),
            low=Decimal("399.25"),
            close=Decimal("401.00"),
            volume=5000000,
            vwap=Decimal("400.75"),
            trade_count=50000,
        )

        proto = bar.to_proto()
        assert isinstance(proto, market_data_pb2.BarData)

        restored = BarData.from_proto(proto)
        assert restored.symbol == bar.symbol
        assert_decimal_equal(restored.open, bar.open)
        assert_decimal_equal(restored.high, bar.high)
        assert_decimal_equal(restored.low, bar.low)
        assert_decimal_equal(restored.close, bar.close)
        assert restored.volume == bar.volume
        assert_decimal_equal(restored.vwap, bar.vwap)
        assert restored.trade_count == bar.trade_count

    def test_bar_data_is_bullish_property(self):
        """Test is_bullish property."""
        # Bullish bar (close > open)
        bullish_bar = BarDataFactory(open=Decimal("100"), close=Decimal("105"))
        assert bullish_bar.close > bullish_bar.open

        # Bearish bar (close < open)
        bearish_bar = BarDataFactory(open=Decimal("100"), close=Decimal("95"))
        assert bearish_bar.close < bearish_bar.open

        # Doji bar (close == open)
        doji_bar = BarDataFactory(open=Decimal("100"), close=Decimal("100"))
        assert doji_bar.close == doji_bar.open

    def test_bar_data_gap_detection(self):
        """Test gap detection between bars."""
        # Create two consecutive bars with a gap
        bar1 = BarDataFactory(high=Decimal("100"), low=Decimal("95"), close=Decimal("98"))

        bar2 = BarDataFactory(open=Decimal("102"), high=Decimal("105"), low=Decimal("101"))  # Gap up from previous close

        gap_size = bar2.open - bar1.close
        assert_decimal_equal(gap_size, Decimal("4"))

    def test_bar_data_edge_cases(self):
        """Test bar data edge cases."""
        # Single price bar (all OHLC same)
        single_price_bar = BarDataFactory(open=Decimal("100"), high=Decimal("100"), low=Decimal("100"), close=Decimal("100"))
        assert single_price_bar.open == single_price_bar.high == single_price_bar.low == single_price_bar.close

        # Zero volume bar
        zero_volume_bar = BarDataFactory(volume=0)
        assert zero_volume_bar.volume == 0

        # No VWAP
        no_vwap_bar = BarDataFactory(vwap=None)
        assert no_vwap_bar.vwap is None


class TestOptionGreeks:
    """Test OptionGreeks model functionality."""

    def test_option_greeks_creation_with_factory(self):
        """Test creating option greeks with factory."""
        greeks = OptionGreeksFactory()

        assert greeks.symbol
        assert greeks.underlying
        assert greeks.option_type in [OptionType.CALL, OptionType.PUT]
        assert greeks.strike > 0
        assert greeks.expiration

        # Greeks should be in reasonable ranges
        assert -1 <= greeks.delta <= 1
        assert greeks.gamma >= 0
        assert greeks.theta <= 0  # Time decay is negative
        assert greeks.vega >= 0
        assert -1 <= greeks.rho <= 1

    def test_option_greeks_delta_by_type(self):
        """Test delta values are appropriate for option type."""
        # Call option delta should be positive
        call_greeks = OptionGreeksFactory(option_type=OptionType.CALL, delta=Decimal("0.55"))
        assert call_greeks.delta > 0

        # Put option delta should be negative
        put_greeks = OptionGreeksFactory(option_type=OptionType.PUT, delta=Decimal("-0.45"))
        assert put_greeks.delta < 0

    def test_option_greeks_proto_conversion(self):
        """Test option greeks proto conversion preserves available data."""
        from tektii.strategy.grpc import market_data_pb2

        greeks = OptionGreeksFactory(
            symbol="AAPL230120C00150000",
            underlying="AAPL",
            option_type=OptionType.CALL,
            strike=Decimal("150"),
            delta=Decimal("0.55"),
            gamma=Decimal("0.02"),
            theta=Decimal("-0.05"),
            vega=Decimal("0.15"),
            rho=Decimal("0.08"),
            underlying_price=Decimal("152.50"),
            implied_volatility=Decimal("0.25"),
            theoretical_value=Decimal("5.75"),
            days_to_expiry=30,
        )

        proto = greeks.to_proto()
        assert isinstance(proto, market_data_pb2.OptionGreeks)

        restored = OptionGreeks.from_proto(proto)
        assert restored.symbol == greeks.symbol
        # Note: underlying, option_type, strike, expiration are not in proto
        assert restored.underlying == "UNKNOWN"
        assert restored.option_type == OptionType.CALL
        assert_decimal_equal(restored.strike, Decimal("100"))
        # These fields are preserved
        assert_decimal_equal(restored.delta, greeks.delta)
        assert_decimal_equal(restored.gamma, greeks.gamma)
        assert_decimal_equal(restored.theta, greeks.theta)
        assert_decimal_equal(restored.vega, greeks.vega)
        assert_decimal_equal(restored.rho, greeks.rho)
        assert_decimal_equal(restored.implied_volatility, greeks.implied_volatility)
        assert_decimal_equal(restored.theoretical_value, greeks.theoretical_value)
        assert_decimal_equal(restored.underlying_price, greeks.underlying_price)
        assert restored.days_to_expiry == greeks.days_to_expiry

    def test_option_greeks_moneyness(self):
        """Test option moneyness calculation."""
        underlying_price = Decimal("150")

        # ITM Call
        itm_call = OptionGreeksFactory(option_type=OptionType.CALL, strike=Decimal("140"), underlying_price=underlying_price)
        assert itm_call.is_itm

        # OTM Call
        otm_call = OptionGreeksFactory(option_type=OptionType.CALL, strike=Decimal("160"), underlying_price=underlying_price)
        assert not otm_call.is_itm

        # ITM Put
        itm_put = OptionGreeksFactory(option_type=OptionType.PUT, strike=Decimal("160"), underlying_price=underlying_price)
        assert itm_put.is_itm

        # ATM Option
        atm_option = OptionGreeksFactory(strike=underlying_price, underlying_price=underlying_price)
        assert atm_option.strike == atm_option.underlying_price

    def test_option_greeks_intrinsic_value(self):
        """Test intrinsic value calculation."""
        # ITM Call
        call = OptionGreeksFactory(option_type=OptionType.CALL, strike=Decimal("140"), underlying_price=Decimal("150"))
        intrinsic_value = max(call.underlying_price - call.strike, Decimal("0"))
        assert_decimal_equal(intrinsic_value, Decimal("10"))

        # OTM Call (no intrinsic value)
        otm_call = OptionGreeksFactory(option_type=OptionType.CALL, strike=Decimal("160"), underlying_price=Decimal("150"))
        intrinsic_value = max(otm_call.underlying_price - otm_call.strike, Decimal("0"))
        assert_decimal_equal(intrinsic_value, Decimal("0"))

    def test_option_greeks_time_value(self):
        """Test time value calculation."""
        greeks = OptionGreeksFactory(
            option_type=OptionType.CALL, strike=Decimal("140"), underlying_price=Decimal("150"), theoretical_value=Decimal("12.50")
        )

        intrinsic_value = max(greeks.underlying_price - greeks.strike, Decimal("0"))
        time_value = greeks.theoretical_value - intrinsic_value
        assert_decimal_equal(time_value, Decimal("2.50"))

    def test_option_greeks_edge_cases(self):
        """Test option greeks edge cases."""
        # Zero IV
        zero_iv = OptionGreeksFactory(implied_volatility=Decimal("0"))
        assert zero_iv.implied_volatility == Decimal("0")

        # Very high IV
        high_iv = OptionGreeksFactory(implied_volatility=Decimal("2.5"))
        assert high_iv.implied_volatility == Decimal("2.5")

        # Deep ITM option (delta near 1 or -1)
        deep_itm_call = OptionGreeksFactory(option_type=OptionType.CALL, strike=Decimal("50"), underlying_price=Decimal("150"), delta=Decimal("0.99"))
        assert deep_itm_call.delta > Decimal("0.95")
        assert deep_itm_call.is_itm

        # Near expiration (high gamma, high theta)
        near_expiry = OptionGreeksFactory(days_to_expiry=1, gamma=Decimal("0.5"), theta=Decimal("-2.0"))
        assert near_expiry.gamma > Decimal("0.3")
        assert near_expiry.theta < Decimal("-1.0")
        assert near_expiry.days_to_expiry == 1
