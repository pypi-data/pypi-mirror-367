"""Edge case generators for comprehensive testing."""

import time
from decimal import Decimal
from typing import Dict, Generator, List, Tuple

from tektii.strategy.grpc import common_pb2, orders_pb2
from tektii.strategy.models.market_data import TickData
from tektii.strategy.models.orders import Order, OrderBuilder


class EdgeCaseGenerator:
    """Generate edge case scenarios for testing."""

    @staticmethod
    def extreme_price_movements() -> List[Tuple[str, List[Decimal]]]:
        """Generate extreme price movement scenarios (circuit breakers).

        Returns:
            List of (scenario_name, price_sequence) tuples
        """
        scenarios = []

        # Flash crash - 10% drop in seconds
        flash_crash = [
            Decimal("100.00"),
            Decimal("99.50"),
            Decimal("98.00"),
            Decimal("95.00"),
            Decimal("90.00"),  # -10% circuit breaker
            Decimal("90.00"),  # Halted
            Decimal("91.00"),  # Recovery begins
            Decimal("93.00"),
            Decimal("95.00"),
        ]
        scenarios.append(("flash_crash", flash_crash))

        # Melt up - rapid price increase
        melt_up = [
            Decimal("100.00"),
            Decimal("101.00"),
            Decimal("103.00"),
            Decimal("106.00"),
            Decimal("110.00"),  # +10% circuit breaker
            Decimal("110.00"),  # Halted
            Decimal("109.50"),  # Slight pullback
            Decimal("109.00"),
        ]
        scenarios.append(("melt_up", melt_up))

        # Gap up/down scenarios
        gap_up = [
            Decimal("100.00"),  # Close
            Decimal("105.00"),  # Gap up open
            Decimal("104.50"),
            Decimal("105.50"),
        ]
        scenarios.append(("gap_up", gap_up))

        gap_down = [
            Decimal("100.00"),  # Close
            Decimal("95.00"),  # Gap down open
            Decimal("94.50"),
            Decimal("95.50"),
        ]
        scenarios.append(("gap_down", gap_down))

        # Extreme volatility
        volatile = [
            Decimal("100.00"),
            Decimal("102.00"),
            Decimal("98.00"),
            Decimal("103.00"),
            Decimal("96.00"),
            Decimal("104.00"),
            Decimal("95.00"),
            Decimal("105.00"),
        ]
        scenarios.append(("extreme_volatility", volatile))

        return scenarios

    @staticmethod
    def zero_liquidity_scenarios() -> List[TickData]:
        """Generate market data with zero or very low liquidity.

        Returns:
            List of TickData with liquidity edge cases
        """
        scenarios = []
        base_time = int(time.time() * 1_000_000)

        # No bid
        no_bid = TickData(symbol="ILLIQUID1", timestamp_us=base_time, last=Decimal("100.00"), bid=None, ask=Decimal("100.10"), volume=0)  # No buyers
        scenarios.append(no_bid)

        # No ask
        no_ask = TickData(
            symbol="ILLIQUID2", timestamp_us=base_time + 1000, last=Decimal("100.00"), bid=Decimal("99.90"), ask=None, volume=0  # No sellers
        )
        scenarios.append(no_ask)

        # Wide spread
        wide_spread = TickData(
            symbol="WIDESPREAD",
            timestamp_us=base_time + 2000,
            last=Decimal("100.00"),
            bid=Decimal("95.00"),  # $5 spread!
            ask=Decimal("105.00"),
            volume=10,  # Very low volume
        )
        scenarios.append(wide_spread)

        # Locked market (bid = ask)
        locked = TickData(
            symbol="LOCKED",
            timestamp_us=base_time + 3000,
            last=Decimal("100.00"),
            bid=Decimal("100.00"),
            ask=Decimal("100.00"),  # Locked
            volume=1000,
        )
        scenarios.append(locked)

        # Crossed market (bid > ask) - should never happen
        crossed = TickData(
            symbol="CROSSED", timestamp_us=base_time + 4000, last=Decimal("100.00"), bid=Decimal("100.10"), ask=Decimal("99.90"), volume=0  # Crossed!
        )
        scenarios.append(crossed)

        return scenarios

    @staticmethod
    def partial_fill_sequences() -> List[List[Tuple[Decimal, Decimal]]]:
        """Generate partial fill sequences for order execution.

        Returns:
            List of fill sequences, each containing (quantity, price) tuples
        """
        sequences = []

        # Many small fills
        small_fills = [
            (Decimal("10"), Decimal("100.00")),
            (Decimal("5"), Decimal("100.01")),
            (Decimal("15"), Decimal("100.02")),
            (Decimal("20"), Decimal("100.01")),
            (Decimal("10"), Decimal("100.03")),
            (Decimal("40"), Decimal("100.02")),
        ]
        sequences.append(small_fills)

        # Price improvement fills
        improving_fills = [
            (Decimal("25"), Decimal("100.00")),
            (Decimal("25"), Decimal("99.99")),  # Better price
            (Decimal("25"), Decimal("99.98")),  # Even better
            (Decimal("25"), Decimal("99.97")),  # Best price
        ]
        sequences.append(improving_fills)

        # Deteriorating fills (slippage)
        slippage_fills = [
            (Decimal("100"), Decimal("100.00")),
            (Decimal("200"), Decimal("100.05")),  # Worse price
            (Decimal("300"), Decimal("100.10")),  # Even worse
            (Decimal("400"), Decimal("100.15")),  # Significant slippage
        ]
        sequences.append(slippage_fills)

        # Single large fill after many attempts
        delayed_fill = [
            (Decimal("0"), Decimal("0")),  # No fill
            (Decimal("0"), Decimal("0")),  # No fill
            (Decimal("0"), Decimal("0")),  # No fill
            (Decimal("1000"), Decimal("100.00")),  # Full fill
        ]
        sequences.append(delayed_fill)

        # Odd lot fills
        odd_lots = [
            (Decimal("1"), Decimal("100.00")),
            (Decimal("99"), Decimal("100.01")),
            (Decimal("7"), Decimal("100.00")),
            (Decimal("93"), Decimal("100.02")),
        ]
        sequences.append(odd_lots)

        return sequences

    @staticmethod
    def rapid_order_modifications() -> List[Dict[str, any]]:
        """Generate rapid order modification sequences.

        Returns:
            List of modification dictionaries
        """
        modifications = []

        # Rapid price changes
        for i in range(10):
            mod = {"type": "price", "new_limit": Decimal("100.00") + Decimal(str(i)) * Decimal("0.01"), "delay_ms": 10}  # 10ms between modifications
            modifications.append(mod)

        # Rapid quantity changes
        for i in range(5):
            mod = {"type": "quantity", "new_quantity": Decimal(str(100 - i * 10)), "delay_ms": 5}
            modifications.append(mod)

        # Mixed modifications
        mod_types = ["price", "quantity", "both"]
        for i in range(20):
            mod = {
                "type": mod_types[i % 3],
                "new_limit": Decimal("99.50") + Decimal(str(i)) * Decimal("0.05"),
                "new_quantity": Decimal(str(50 + i * 5)),
                "delay_ms": 1,  # Very rapid
            }
            modifications.append(mod)

        return modifications

    @staticmethod
    def market_data_gaps() -> Generator[TickData, None, None]:
        """Generate market data with gaps and corrections.

        Yields:
            TickData with various gap scenarios
        """
        base_time = int(time.time() * 1_000_000)
        base_price = Decimal("100.00")

        # Normal ticks
        for i in range(5):
            yield TickData(
                symbol="GAPPY",
                timestamp_us=base_time + i * 1000,
                last=base_price + Decimal(str(i)) * Decimal("0.01"),
                bid=base_price + Decimal(str(i)) * Decimal("0.01") - Decimal("0.01"),
                ask=base_price + Decimal(str(i)) * Decimal("0.01") + Decimal("0.01"),
                volume=1000,
            )

        # 5 second gap
        gap_time = base_time + 5_000_000

        # Price jump after gap
        yield TickData(
            symbol="GAPPY",
            timestamp_us=gap_time,
            last=base_price + Decimal("2.00"),  # $2 jump
            bid=base_price + Decimal("1.95"),
            ask=base_price + Decimal("2.05"),
            volume=5000,
        )

        # Correction tick
        yield TickData(
            symbol="GAPPY",
            timestamp_us=gap_time + 1000,
            last=base_price + Decimal("0.50"),  # Corrected price
            bid=base_price + Decimal("0.49"),
            ask=base_price + Decimal("0.51"),
            volume=2000,
            # Could add a correction flag here
        )

        # Another gap with no data
        for i in range(10):
            # 10 seconds of no data
            pass

        # Resume with normal data
        resume_time = gap_time + 10_000_000
        yield TickData(
            symbol="GAPPY",
            timestamp_us=resume_time,
            last=base_price + Decimal("0.55"),
            bid=base_price + Decimal("0.54"),
            ask=base_price + Decimal("0.56"),
            volume=1500,
        )

    @staticmethod
    def extreme_decimal_values() -> List[Decimal]:
        """Generate extreme decimal values for testing precision.

        Returns:
            List of extreme decimal values
        """
        values = [
            # Very small values
            Decimal("0.000001"),  # 1 micro
            Decimal("0.0001"),  # 1 basis point
            Decimal("0.01"),  # 1 cent
            # Very large values
            Decimal("999999.99"),
            Decimal("1000000.00"),
            Decimal("10000000.00"),
            # Maximum precision (6 decimal places)
            Decimal("123.456789"),
            Decimal("0.123456"),
            Decimal("9999.999999"),
            # Common edge values
            Decimal("1.0"),
            Decimal("0.0"),  # Zero
            Decimal("-1.0"),  # Negative (for P&L)
            # Fractional shares
            Decimal("0.5"),
            Decimal("0.25"),
            Decimal("0.125"),
            Decimal("1.333333"),
            # Typical crypto prices
            Decimal("0.00000100"),  # Satoshi levels
            Decimal("50000.00"),  # BTC levels
            # Stress test values
            Decimal("999999.999999"),  # Max both sides
            Decimal("0.000001"),  # Min positive
        ]

        return values

    @staticmethod
    def malformed_order_requests() -> List[orders_pb2.PlaceOrderRequest]:
        """Generate malformed order requests for validation testing.

        Returns:
            List of invalid order requests
        """
        requests = []

        # Empty symbol
        requests.append(
            orders_pb2.PlaceOrderRequest(symbol="", side=common_pb2.ORDER_SIDE_BUY, order_type=common_pb2.ORDER_TYPE_MARKET, quantity=100.0)
        )

        # Negative quantity
        requests.append(
            orders_pb2.PlaceOrderRequest(symbol="AAPL", side=common_pb2.ORDER_SIDE_BUY, order_type=common_pb2.ORDER_TYPE_MARKET, quantity=-100.0)
        )

        # Zero quantity
        requests.append(
            orders_pb2.PlaceOrderRequest(symbol="AAPL", side=common_pb2.ORDER_SIDE_BUY, order_type=common_pb2.ORDER_TYPE_MARKET, quantity=0.0)
        )

        # Limit order without price
        requests.append(
            orders_pb2.PlaceOrderRequest(
                symbol="AAPL", side=common_pb2.ORDER_SIDE_BUY, order_type=common_pb2.ORDER_TYPE_LIMIT, quantity=100.0, limit_price=0.0  # Invalid
            )
        )

        # Stop order without stop price
        requests.append(
            orders_pb2.PlaceOrderRequest(
                symbol="AAPL", side=common_pb2.ORDER_SIDE_BUY, order_type=common_pb2.ORDER_TYPE_STOP, quantity=100.0, stop_price=0.0  # Invalid
            )
        )

        # Very long symbol
        requests.append(
            orders_pb2.PlaceOrderRequest(
                symbol="A" * 100, side=common_pb2.ORDER_SIDE_BUY, order_type=common_pb2.ORDER_TYPE_MARKET, quantity=100.0  # 100 character symbol
            )
        )

        # Invalid enum values (if possible)
        requests.append(
            orders_pb2.PlaceOrderRequest(symbol="AAPL", side=999, order_type=common_pb2.ORDER_TYPE_MARKET, quantity=100.0)  # Invalid side
        )

        # Extreme quantity
        requests.append(
            orders_pb2.PlaceOrderRequest(
                symbol="AAPL", side=common_pb2.ORDER_SIDE_BUY, order_type=common_pb2.ORDER_TYPE_MARKET, quantity=1e10  # 10 billion shares
            )
        )

        # NaN/Inf values (if float allows)
        requests.append(
            orders_pb2.PlaceOrderRequest(
                symbol="AAPL", side=common_pb2.ORDER_SIDE_BUY, order_type=common_pb2.ORDER_TYPE_LIMIT, quantity=100.0, limit_price=float("inf")
            )
        )

        return requests

    @staticmethod
    def concurrent_order_scenarios() -> List[List[Order]]:
        """Generate concurrent order scenarios for race condition testing.

        Returns:
            List of order lists that should be processed concurrently
        """
        scenarios = []

        # Multiple orders for same symbol
        same_symbol = []
        for i in range(10):
            order = OrderBuilder().symbol("RACE").buy() if i % 2 == 0 else OrderBuilder().symbol("RACE").sell().market().quantity(100).build()
            same_symbol.append(order)
        scenarios.append(same_symbol)

        # Conflicting limit orders
        conflicting = [
            OrderBuilder().symbol("CONF").buy().limit(Decimal("100.00")).quantity(100).build(),
            OrderBuilder().symbol("CONF").buy().limit(Decimal("100.01")).quantity(100).build(),
            OrderBuilder().symbol("CONF").sell().limit(Decimal("100.00")).quantity(100).build(),
            OrderBuilder().symbol("CONF").sell().limit(Decimal("99.99")).quantity(100).build(),
        ]
        scenarios.append(conflicting)

        # Order and immediate cancel
        order_cancel = [
            OrderBuilder().symbol("CANCEL").buy().limit(Decimal("100.00")).quantity(1000).build(),
            # Cancel order would be sent immediately after
        ]
        scenarios.append(order_cancel)

        # Bracket orders (entry + stop loss + take profit)
        bracket = [
            OrderBuilder().symbol("BRACKET").buy().market().quantity(100).build(),
            OrderBuilder().symbol("BRACKET").sell().stop(Decimal("95.00")).quantity(100).build(),
            OrderBuilder().symbol("BRACKET").sell().limit(Decimal("105.00")).quantity(100).build(),
        ]
        scenarios.append(bracket)

        return scenarios


class MarketAnomalyGenerator:
    """Generate market anomaly scenarios for robust testing."""

    @staticmethod
    def generate_fat_finger_trade() -> TickData:
        """Generate a fat finger trade (order of magnitude price error)."""
        return TickData(
            symbol="FATFINGER",
            timestamp_us=int(time.time() * 1_000_000),
            last=Decimal("10.00"),  # Should be $100.00
            bid=Decimal("99.90"),  # Normal bid
            ask=Decimal("100.10"),  # Normal ask
            volume=100000,  # Large volume at wrong price
        )

    @staticmethod
    def generate_quote_stuffing() -> Generator[TickData, None, None]:
        """Generate quote stuffing scenario (rapid quote updates)."""
        base_time = int(time.time() * 1_000_000)
        base_price = Decimal("100.00")

        # 1000 quotes in 1 second
        for i in range(1000):
            yield TickData(
                symbol="STUFFED",
                timestamp_us=base_time + i * 1000,  # 1ms apart
                last=base_price,
                bid=base_price - Decimal("0.01") + Decimal(str(i % 10)) * Decimal("0.001"),
                ask=base_price + Decimal("0.01") + Decimal(str(i % 10)) * Decimal("0.001"),
                volume=0,  # No actual trades
            )

    @staticmethod
    def generate_market_manipulation_patterns() -> Dict[str, List[TickData]]:
        """Generate patterns that might indicate market manipulation."""
        patterns = {}
        base_time = int(time.time() * 1_000_000)

        # Spoofing pattern - large orders that disappear
        spoofing = []
        for i in range(10):
            tick = TickData(
                symbol="SPOOF",
                timestamp_us=base_time + i * 1000,
                last=Decimal("100.00"),
                bid=Decimal("99.95") if i < 5 else Decimal("99.90"),  # Bid disappears
                ask=Decimal("100.05"),
                volume=100 if i == 5 else 0,  # Small trade when bid pulled
            )
            spoofing.append(tick)
        patterns["spoofing"] = spoofing

        # Wash trading - buy and sell at same price
        wash = []
        for i in range(20):
            tick = TickData(
                symbol="WASH",
                timestamp_us=base_time + i * 500,
                last=Decimal("100.00"),  # Price doesn't move
                bid=Decimal("99.99"),
                ask=Decimal("100.01"),
                volume=1000,  # High volume but no price movement
            )
            wash.append(tick)
        patterns["wash_trading"] = wash

        # Pump and dump pattern
        pump_dump = []
        # Pump phase
        for i in range(10):
            price = Decimal("10.00") + Decimal(str(i)) * Decimal("0.50")
            tick = TickData(
                symbol="PUMP",
                timestamp_us=base_time + i * 1000,
                last=price,
                bid=price - Decimal("0.01"),
                ask=price + Decimal("0.01"),
                volume=10000 * (i + 1),  # Increasing volume
            )
            pump_dump.append(tick)
        # Dump phase
        for i in range(10):
            price = Decimal("15.00") - Decimal(str(i)) * Decimal("1.00")
            tick = TickData(
                symbol="PUMP",
                timestamp_us=base_time + (10 + i) * 1000,
                last=price,
                bid=price - Decimal("0.05"),  # Wider spread
                ask=price + Decimal("0.05"),
                volume=5000,  # Lower volume
            )
            pump_dump.append(tick)
        patterns["pump_and_dump"] = pump_dump

        return patterns
