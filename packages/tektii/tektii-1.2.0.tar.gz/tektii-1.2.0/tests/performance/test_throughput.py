"""Performance benchmarks for throughput testing."""

import time
from decimal import Decimal

import pytest

from tektii.strategy.grpc import common_pb2, orders_pb2
from tektii.strategy.models.enums import OrderSide, OrderStatus, OrderType
from tektii.strategy.models.events import OrderUpdateEvent, TektiiEvent
from tektii.strategy.models.market_data import TickData
from tektii.strategy.models.orders import Order, OrderBuilder
from tektii.testing.mock_broker import MockBrokerService
from tektii.testing.realistic_broker import RealisticMockBroker

# Proto conversions are methods on the Order class
from tests.factories.market_data import TickDataFactory


class TestOrderCreationThroughput:
    """Benchmark order creation and validation performance."""

    def test_order_builder_throughput(self, benchmark):
        """Test OrderBuilder can create 100k orders/sec."""

        def create_orders():
            orders = []
            for i in range(1000):
                order = OrderBuilder().symbol("AAPL").buy().market().quantity(100).build()
                orders.append(order)
            return orders

        # Benchmark should complete 1000 orders quickly
        result = benchmark(create_orders)

        # Assert we can create at least 100k orders/sec
        # 1000 orders should take less than 10ms
        assert benchmark.stats["mean"] < 0.01
        assert len(result) == 1000

    def test_order_validation_throughput(self, benchmark):
        """Test order validation speed."""

        # Pre-create orders
        orders = []
        for i in range(1000):
            builder = OrderBuilder().symbol(f"TEST{i%10}")

            if i % 2 == 0:
                builder.buy()
            else:
                builder.sell()

            if i % 3 == 0:
                builder.limit(Decimal("100.50"))
            else:
                builder.market()

            builder.quantity(Decimal(str((i % 100) + 1)))
            order = builder.build()
            orders.append(order)

        def validate_orders():
            for order in orders:
                # Validation happens in the builder
                assert order.symbol
                assert order.quantity > 0
                if order.order_type == common_pb2.ORDER_TYPE_LIMIT:
                    assert order.limit_price > 0

        benchmark(validate_orders)

        # Should validate 1000 orders in less than 5ms
        assert benchmark.stats["mean"] < 0.005

    @pytest.mark.parametrize("order_count", [100, 1000, 10000])
    def test_batch_order_creation_scaling(self, benchmark, order_count):
        """Test how order creation scales with batch size."""

        def create_batch():
            orders = []
            for i in range(order_count):
                order = OrderBuilder().symbol("SPY").buy().limit(Decimal("450.00")).quantity(10).build()
                orders.append(order)
            return orders

        benchmark(create_batch)

        # Should scale linearly - 10x orders should take ~10x time
        # Allow 20% overhead for larger batches
        if order_count == 100:
            assert benchmark.stats["mean"] < 0.001
        elif order_count == 1000:
            assert benchmark.stats["mean"] < 0.012
        else:  # 10000
            assert benchmark.stats["mean"] < 0.15


class TestProtoConversionThroughput:
    """Benchmark proto conversion performance."""

    def test_order_to_proto_throughput(self, benchmark):
        """Test conversion of Order to proto (target: <10μs per conversion)."""

        # Pre-create diverse Order objects
        orders = []
        ts = int(time.time() * 1_000_000)
        for i in range(1000):
            base_order = {
                "order_id": f"TEST-{i:06d}",
                "symbol": f"TEST{i}",
                "quantity": Decimal("100"),
                "status": OrderStatus.PENDING,
                "created_at_us": ts + i,
            }

            if i % 4 == 0:
                order = Order(
                    **base_order,
                    side=OrderSide.BUY,
                    order_type=OrderType.MARKET,
                )
            elif i % 4 == 1:
                order = Order(
                    **base_order,
                    side=OrderSide.SELL,
                    order_type=OrderType.LIMIT,
                    limit_price=Decimal("99.99"),
                )
            elif i % 4 == 2:
                order = Order(
                    **base_order,
                    side=OrderSide.BUY,
                    order_type=OrderType.STOP,
                    stop_price=Decimal("101.00"),
                )
            else:
                order = Order(
                    **base_order,
                    side=OrderSide.SELL,
                    order_type=OrderType.STOP_LIMIT,
                    stop_price=Decimal("98.00"),
                    limit_price=Decimal("97.50"),
                )

            orders.append(order)

        def convert_to_proto():
            protos = []
            for order in orders:
                proto = order.to_proto()
                protos.append(proto)
            return protos

        result = benchmark(convert_to_proto)

        # 1000 conversions should take less than 10ms (10μs each)
        assert benchmark.stats["mean"] < 0.01
        assert len(result) == 1000

    def test_proto_to_order_throughput(self, benchmark):
        """Test conversion of proto to Order."""

        # Pre-create proto orders
        protos = []
        for i in range(1000):
            proto = common_pb2.Order(
                order_id=f"TEST-{i:06d}",
                symbol=f"SYM{i%10}",
                status=common_pb2.ORDER_STATUS_FILLED,
                side=common_pb2.ORDER_SIDE_BUY if i % 2 == 0 else common_pb2.ORDER_SIDE_SELL,
                order_type=common_pb2.ORDER_TYPE_LIMIT if i % 3 == 0 else common_pb2.ORDER_TYPE_MARKET,
                quantity=float((i % 100) + 1),
                filled_quantity=float((i % 100) + 1),
                limit_price=100.0 if i % 3 == 0 else 0.0,
                created_at_us=int(time.time() * 1_000_000),
            )
            protos.append(proto)

        def convert_from_proto():
            orders = []
            for proto in protos:
                order = Order.from_proto(proto)
                orders.append(order)
            return orders

        result = benchmark(convert_from_proto)

        # Should be comparable to to_proto conversion
        assert benchmark.stats["mean"] < 0.015
        assert len(result) == 1000

    def test_round_trip_conversion(self, benchmark):
        """Test full round-trip conversion performance."""

        # Create initial Order objects
        orders = []
        ts = int(time.time() * 1_000_000)
        for i in range(500):
            if i % 2 == 0:
                order = Order(
                    order_id=f"RT-{i:06d}",
                    symbol=f"RT{i}",
                    side=OrderSide.BUY,
                    order_type=OrderType.MARKET,
                    quantity=Decimal("100"),
                    status=OrderStatus.PENDING,
                    created_at_us=ts + i,
                )
            elif i % 3 == 0:
                order = Order(
                    order_id=f"RT-{i:06d}",
                    symbol=f"RT{i}",
                    side=OrderSide.SELL,
                    order_type=OrderType.MARKET,
                    quantity=Decimal("100"),
                    status=OrderStatus.PENDING,
                    created_at_us=ts + i,
                )
            else:
                order = Order(
                    order_id=f"RT-{i:06d}",
                    symbol=f"RT{i}",
                    side=OrderSide.BUY,
                    order_type=OrderType.LIMIT,
                    quantity=Decimal("50"),
                    limit_price=Decimal("100.00"),
                    status=OrderStatus.PENDING,
                    created_at_us=ts + i,
                )
            orders.append(order)

        def round_trip():
            results = []
            for order in orders:
                proto = order.to_proto()
                restored = Order.from_proto(proto)
                results.append(restored)
            return results

        result = benchmark(round_trip)

        # Round trip should be efficient
        assert benchmark.stats["mean"] < 0.02
        assert len(result) == 500


class TestStrategyEventThroughput:
    """Benchmark strategy event processing performance."""

    def test_market_data_event_processing(self, benchmark):
        """Test strategy can process 10k market events/sec."""

        # Create a simple strategy that counts events
        class CountingStrategy:
            def __init__(self):
                self.event_count = 0

            def on_market_data(self, event: TektiiEvent) -> None:
                self.event_count += 1
                # Minimal processing
                if event.tick_data and event.tick_data.last > Decimal("150"):
                    pass

        # Pre-create events
        events = []
        for i in range(10000):
            tick = TickData(
                symbol="AAPL",
                timestamp_us=int(time.time() * 1_000_000) + i,
                last=Decimal("150.00") + Decimal(str(i % 10)) / 100,
                bid=Decimal("149.99"),
                ask=Decimal("150.01"),
                volume=1000 + i,
            )
            # Create a simple event wrapper
            event = TektiiEvent(event_id=f"TEST-{i:06d}", timestamp_us=tick.timestamp_us, tick_data=tick)
            events.append(event)

        def process_events():
            local_strategy = CountingStrategy()
            for event in events:
                local_strategy.on_market_data(event)
            return local_strategy.event_count

        result = benchmark(process_events)

        # Should process 10k events in less than 1 second
        assert benchmark.stats["mean"] < 1.0
        assert result == 10000

    def test_order_update_event_processing(self, benchmark):
        """Test order update event processing speed."""

        class OrderTracker:
            def __init__(self):
                self.updates = 0
                self.fills = 0

            def on_order_update(self, event: OrderUpdateEvent) -> None:
                self.updates += 1
                if event.status == OrderStatus.FILLED:
                    self.fills += 1

        # Pre-create order update events
        events = []
        ts = int(time.time() * 1_000_000)
        for i in range(5000):
            event = OrderUpdateEvent(
                order_id=f"ORD-{i:06d}",
                symbol="SPY",
                side=OrderSide.BUY,
                order_type=OrderType.MARKET,
                quantity=Decimal("100"),
                status=OrderStatus.FILLED if i % 2 == 0 else OrderStatus.SUBMITTED,
                filled_quantity=Decimal("100") if i % 2 == 0 else Decimal("0"),
                remaining_quantity=Decimal("0") if i % 2 == 0 else Decimal("100"),
                avg_fill_price=Decimal("450.05") if i % 2 == 0 else None,
                created_at_us=ts,
                updated_at_us=ts + i,
            )
            events.append(event)

        def process_updates():
            local_tracker = OrderTracker()
            for event in events:
                local_tracker.on_order_update(event)
            return (local_tracker.updates, local_tracker.fills)

        result = benchmark(process_updates)

        # Should handle 5k updates quickly
        assert benchmark.stats["mean"] < 0.1
        assert result[0] == 5000
        assert result[1] == 2500


class TestBrokerThroughput:
    """Benchmark broker service throughput."""

    def test_mock_broker_order_placement(self, benchmark):
        """Test mock broker order placement throughput."""

        broker = MockBrokerService()

        # Pre-create order requests
        requests = []
        for i in range(1000):
            request = orders_pb2.PlaceOrderRequest(
                symbol=f"TEST{i%10}", side=common_pb2.ORDER_SIDE_BUY, order_type=common_pb2.ORDER_TYPE_MARKET, quantity=100.0, request_id=f"REQ-{i}"
            )
            requests.append(request)

        def place_orders():
            responses = []
            for request in requests:
                response = broker.PlaceOrder(request, None)
                responses.append(response)
            return responses

        result = benchmark(place_orders)

        # Mock broker should be very fast
        assert benchmark.stats["mean"] < 0.05
        assert len(result) == 1000
        assert all(r.accepted for r in result)

    def test_realistic_broker_with_market_simulation(self, benchmark):
        """Test realistic broker with market simulation."""

        broker = RealisticMockBroker()
        broker.enable_rejections = False

        # Add test symbols
        for i in range(10):
            broker.market_sim.add_symbol(f"PERF{i}", Decimal("100.00"))

        # Pre-create diverse order requests
        requests = []
        for i in range(500):
            request = orders_pb2.PlaceOrderRequest(
                symbol=f"PERF{i%10}",
                side=common_pb2.ORDER_SIDE_BUY if i % 2 == 0 else common_pb2.ORDER_SIDE_SELL,
                order_type=common_pb2.ORDER_TYPE_MARKET if i % 3 == 0 else common_pb2.ORDER_TYPE_LIMIT,
                quantity=float((i % 50) + 10),
                limit_price=99.0 if i % 3 != 0 else 0.0,
                request_id=f"PERF-{i}",
            )
            requests.append(request)

        def simulate_trading():
            responses = []
            for request in requests:
                response = broker.PlaceOrder(request, None)
                responses.append(response)
            return responses

        result = benchmark(simulate_trading)

        # Realistic broker is slower but should still be performant
        assert benchmark.stats["mean"] < 0.2
        assert len(result) == 500


class TestMemoryEfficiency:
    """Test memory usage patterns."""

    def test_order_memory_footprint(self, benchmark):
        """Test memory efficiency of order objects."""

        def create_and_store_orders():
            orders = []
            for i in range(10000):
                order = OrderBuilder().symbol(f"MEM{i%100}").buy().limit(Decimal("100.00") + Decimal(str(i % 100)) / 100).quantity(100).build()
                orders.append(order)
            return orders

        # This also serves as a memory allocation benchmark
        result = benchmark(create_and_store_orders)

        # Should handle 10k orders efficiently
        assert benchmark.stats["mean"] < 0.5
        assert len(result) == 10000

    def test_tick_data_factory_performance(self, benchmark):
        """Test performance of test data generation."""

        def generate_ticks():
            ticks = []
            for _ in range(1000):
                tick = TickDataFactory.build()
                ticks.append(tick)
            return ticks

        result = benchmark(generate_ticks)

        # Factory should be efficient for test data generation
        assert benchmark.stats["mean"] < 0.5
        assert len(result) == 1000
