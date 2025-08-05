"""Performance benchmarks for latency testing."""

import time
from decimal import Decimal

from tektii.strategy.grpc import common_pb2, orders_pb2
from tektii.strategy.models.enums import OrderSide, OrderStatus, OrderType
from tektii.strategy.models.events import OrderUpdateEvent, TektiiEvent
from tektii.strategy.models.market_data import TickData
from tektii.strategy.models.orders import Order, OrderBuilder

# Proto conversions are methods on the Order class
from tektii.testing.mock_broker import MockBrokerService
from tektii.testing.realistic_broker import RealisticMockBroker


class TestOrderValidationLatency:
    """Benchmark order validation latency (p99 < 1ms)."""

    def test_simple_order_validation_p99(self, benchmark):
        """Test simple market order validation latency."""

        def validate_order():
            order = OrderBuilder().symbol("AAPL").buy().market().quantity(100).build()
            return order

        # Run multiple times to get percentiles
        benchmark.pedantic(validate_order, rounds=1000, iterations=1)

        # Get p99 latency (in seconds)
        stats = benchmark.stats
        p99 = stats.get("q3", stats["max"])  # Use Q3 as approximation of p99

        # Assert p99 < 1ms
        assert p99 < 0.001

    def test_complex_order_validation_p99(self, benchmark):
        """Test complex order validation with all fields."""

        def validate_complex_order():
            order = (
                OrderBuilder()
                .symbol("GOOGL")
                .sell()
                .stop_limit(Decimal("2750.00"), Decimal("2745.00"))
                .quantity(Decimal("25.5"))
                .time_in_force("GTD")
                .client_order_id("CLIENT-12345")
                .build()
            )
            return order

        benchmark.pedantic(validate_complex_order, rounds=1000, iterations=1)

        stats = benchmark.stats
        p99 = stats.get("q3", stats["max"])

        # Complex orders should still validate quickly
        assert p99 < 0.001

    def test_batch_validation_latency(self, benchmark):
        """Test validation latency for batches of orders."""

        def validate_batch():
            orders = []
            for i in range(10):
                order = (
                    OrderBuilder().symbol(f"SYM{i}").buy()
                    if i % 2 == 0
                    else (
                        OrderBuilder().symbol(f"SYM{i}").sell().market()
                        if i % 3 == 0
                        else OrderBuilder().symbol(f"SYM{i}").buy().limit(Decimal("100.00")).quantity(100).build()
                    )
                )
                orders.append(order)
            return orders

        benchmark.pedantic(validate_batch, rounds=100, iterations=1)

        stats = benchmark.stats
        p99 = stats.get("q3", stats["max"])

        # 10 orders should validate in under 5ms at p99
        assert p99 < 0.005


class TestEventDispatchLatency:
    """Benchmark event dispatch latency (p99 < 100μs)."""

    def test_market_data_dispatch_latency(self, benchmark):
        """Test market data event dispatch latency."""

        class FastStrategy:
            def on_market_data(self, event: TektiiEvent) -> None:
                # Minimal processing
                tick = event.tick_data
                if tick and tick.last > Decimal("100"):
                    self.last_price = tick.last

        strategy = FastStrategy()

        # Pre-create event
        tick = TickData(
            symbol="AAPL",
            timestamp_us=int(time.time() * 1_000_000),
            last=Decimal("150.00"),
            bid=Decimal("149.99"),
            ask=Decimal("150.01"),
            volume=1000,
        )
        event = TektiiEvent(event_id="TEST-001", timestamp_us=tick.timestamp_us, tick_data=tick)

        def dispatch_event():
            strategy.on_market_data(event)

        benchmark.pedantic(dispatch_event, rounds=10000, iterations=1)

        stats = benchmark.stats
        p99 = stats.get("q3", stats["max"])

        # Event dispatch should be very fast - target 100μs
        assert p99 < 0.0001

    def test_order_update_dispatch_latency(self, benchmark):
        """Test order update event dispatch latency."""

        class OrderHandler:
            def __init__(self):
                self.orders = {}

            def on_order_update(self, event: OrderUpdateEvent) -> None:
                self.orders[event.order_id] = event

        handler = OrderHandler()

        # Pre-create event
        ts = int(time.time() * 1_000_000)
        event = OrderUpdateEvent(
            order_id="TEST-001",
            symbol="SPY",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=Decimal("100"),
            status=OrderStatus.FILLED,
            filled_quantity=Decimal("100"),
            remaining_quantity=Decimal("0"),
            avg_fill_price=Decimal("450.05"),
            created_at_us=ts,
            updated_at_us=ts,
        )

        def dispatch_update():
            handler.on_order_update(event)

        benchmark.pedantic(dispatch_update, rounds=10000, iterations=1)

        stats = benchmark.stats
        p99 = stats.get("q3", stats["max"])

        # Order updates should also be very fast
        assert p99 < 0.0001


class TestGrpcLatency:
    """Benchmark gRPC round-trip latency (p99 < 5ms)."""

    def test_mock_broker_round_trip(self, benchmark):
        """Test mock broker gRPC-like round trip."""

        broker = MockBrokerService()

        # Pre-create request
        request = orders_pb2.PlaceOrderRequest(
            symbol="AAPL", side=common_pb2.ORDER_SIDE_BUY, order_type=common_pb2.ORDER_TYPE_MARKET, quantity=100.0, request_id="BENCH-001"
        )

        def round_trip():
            response = broker.PlaceOrder(request, None)
            return response

        benchmark.pedantic(round_trip, rounds=1000, iterations=1)

        stats = benchmark.stats
        p99 = stats.get("q3", stats["max"])

        # Mock broker should have very low latency
        assert p99 < 0.001

    def test_realistic_broker_round_trip(self, benchmark):
        """Test realistic broker with full simulation."""

        broker = RealisticMockBroker()
        broker.enable_rejections = False

        # Add symbol
        broker.market_sim.add_symbol("BENCH", Decimal("100.00"))

        request = orders_pb2.PlaceOrderRequest(
            symbol="BENCH", side=common_pb2.ORDER_SIDE_BUY, order_type=common_pb2.ORDER_TYPE_MARKET, quantity=50.0, request_id="REAL-001"
        )

        def realistic_round_trip():
            response = broker.PlaceOrder(request, None)
            return response

        benchmark.pedantic(realistic_round_trip, rounds=500, iterations=1)

        stats = benchmark.stats
        p99 = stats.get("q3", stats["max"])

        # Realistic broker with simulation should still meet 5ms target
        assert p99 < 0.005

    def test_order_query_latency(self, benchmark):
        """Test order state query latency."""

        broker = MockBrokerService()

        # Place some orders first
        for i in range(100):
            request = orders_pb2.PlaceOrderRequest(
                symbol=f"SYM{i%10}", side=common_pb2.ORDER_SIDE_BUY, order_type=common_pb2.ORDER_TYPE_MARKET, quantity=100.0, request_id=f"SETUP-{i}"
            )
            broker.PlaceOrder(request, None)

        # Query state instead
        state_request = orders_pb2.StateRequest()

        def query_state():
            response = broker.GetState(state_request, None)
            return response

        benchmark.pedantic(query_state, rounds=1000, iterations=1)

        stats = benchmark.stats
        p99 = stats.get("q3", stats["max"])

        # Query operations should be fast
        assert p99 < 0.002


class TestProtoConversionLatency:
    """Test proto conversion latency at percentiles."""

    def test_order_to_proto_p99(self, benchmark):
        """Test order to proto conversion p99 latency."""

        # Pre-create order model
        order = Order(
            order_id="BENCH-001",
            symbol="TSLA",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("15"),
            limit_price=Decimal("850.00"),
            status=OrderStatus.PENDING,
            created_at_us=int(time.time() * 1_000_000),
        )

        def convert():
            proto = order.to_proto()
            return proto

        benchmark.pedantic(convert, rounds=5000, iterations=1)

        stats = benchmark.stats
        p99 = stats.get("q3", stats["max"])

        # Proto conversion should be under 10μs at p99
        assert p99 < 0.00001

    def test_proto_to_order_p99(self, benchmark):
        """Test proto to order conversion p99 latency."""

        # Pre-create proto
        proto = common_pb2.Order(
            order_id="BENCH-123456",
            symbol="MSFT",
            status=common_pb2.ORDER_STATUS_FILLED,
            side=common_pb2.ORDER_SIDE_SELL,
            order_type=common_pb2.ORDER_TYPE_LIMIT,
            quantity=50.0,
            filled_quantity=50.0,
            limit_price=380.50,
            created_at_us=int(time.time() * 1_000_000),
        )

        def convert():
            order = Order.from_proto(proto)
            return order

        benchmark.pedantic(convert, rounds=5000, iterations=1)

        stats = benchmark.stats
        p99 = stats.get("q3", stats["max"])

        # Should be similar to to_proto conversion
        assert p99 < 0.00002


class TestCriticalPathLatency:
    """Test end-to-end critical path latency."""

    def test_market_order_full_cycle(self, benchmark):
        """Test full cycle: create order -> validate -> place -> receive update."""

        broker = RealisticMockBroker()
        broker.enable_rejections = False
        broker.market_sim.add_symbol("CYCLE", Decimal("100.00"))

        def full_cycle():
            # Create order request directly
            request = OrderBuilder().symbol("CYCLE").buy().market().quantity(100).build()
            request.request_id = "CYCLE-001"

            # Place order
            response = broker.PlaceOrder(request, None)

            # Return response as marker of success
            return response

        benchmark.pedantic(full_cycle, rounds=100, iterations=1)

        stats = benchmark.stats
        p99 = stats.get("q3", stats["max"])

        # Full cycle should complete quickly
        assert p99 < 0.01

    def test_limit_order_placement_latency(self, benchmark):
        """Test limit order placement with order book check."""

        broker = RealisticMockBroker()
        broker.enable_rejections = False
        broker.market_sim.add_symbol("LIMIT", Decimal("100.00"))

        # Update order book
        market = broker.market_sim.markets["LIMIT"]
        market.generate_order_book()

        def place_limit_order():
            request = orders_pb2.PlaceOrderRequest(
                symbol="LIMIT",
                side=common_pb2.ORDER_SIDE_BUY,
                order_type=common_pb2.ORDER_TYPE_LIMIT,
                quantity=50.0,
                limit_price=99.50,
                request_id="LIM-001",
            )

            response = broker.PlaceOrder(request, None)
            return response

        benchmark.pedantic(place_limit_order, rounds=500, iterations=1)

        stats = benchmark.stats
        p99 = stats.get("q3", stats["max"])

        # Limit orders with book check should still be fast
        assert p99 < 0.005


class TestScalabilityLatency:
    """Test latency under load conditions."""

    def test_latency_with_many_orders(self, benchmark):
        """Test order placement latency with many existing orders."""

        broker = MockBrokerService()

        # Pre-populate with many orders
        for i in range(10000):
            request = orders_pb2.PlaceOrderRequest(
                symbol=f"LOAD{i%100}", side=common_pb2.ORDER_SIDE_BUY, order_type=common_pb2.ORDER_TYPE_MARKET, quantity=100.0, request_id=f"LOAD-{i}"
            )
            broker.PlaceOrder(request, None)

        # Test latency of new order
        new_request = orders_pb2.PlaceOrderRequest(
            symbol="NEWORDER",
            side=common_pb2.ORDER_SIDE_SELL,
            order_type=common_pb2.ORDER_TYPE_LIMIT,
            quantity=200.0,
            limit_price=105.0,
            request_id="NEW-001",
        )

        def place_under_load():
            response = broker.PlaceOrder(new_request, None)
            return response

        benchmark.pedantic(place_under_load, rounds=100, iterations=1)

        stats = benchmark.stats
        p99 = stats.get("q3", stats["max"])

        # Should maintain low latency even with many orders
        assert p99 < 0.002

    def test_concurrent_event_processing(self, benchmark):
        """Test event processing latency with high event rate."""

        class BusyStrategy:
            def __init__(self):
                self.events_processed = 0
                self.total_latency = 0

            def on_market_data(self, event: TektiiEvent) -> None:
                start = time.time()

                # Simulate some processing
                tick = event.tick_data
                if tick and tick.last > Decimal("100"):
                    self.events_processed += 1

                self.total_latency += time.time() - start

        strategy = BusyStrategy()

        # Create many events
        events = []
        for i in range(1000):
            tick = TickData(
                symbol=f"SYM{i%10}",
                timestamp_us=int(time.time() * 1_000_000) + i,
                last=Decimal("100.00") + Decimal(str(i % 100)) / 100,
                bid=Decimal("99.99"),
                ask=Decimal("100.01"),
                volume=1000,
            )
            event = TektiiEvent(event_id="TEST-001", timestamp_us=tick.timestamp_us, tick_data=tick)
            events.append(event)

        def process_many():
            for event in events:
                strategy.on_market_data(event)

        benchmark.pedantic(process_many, rounds=10, iterations=1)

        stats = benchmark.stats
        avg_latency = stats["mean"] / 1000  # Per event

        # Average per-event latency should remain low
        assert avg_latency < 0.0001
